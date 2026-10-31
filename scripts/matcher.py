#!/usr/bin/env python3
import re
from collections import Counter, deque
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from terms import Term, normalize_text

SIMPLE_CONTENT_FIELDS = (
    "name",
    "description",
    "authors",
    "productionPlace",
    "findPlace",
    "mainWords",
    "provenance",
    "typologyDesc",
    "technologies",
    "fund",
)
NESTED_CONTENT_FIELDS = (("typology", "name"),)
MUSEUM_FIELD = ("museum", "name")
TOKEN_RE = re.compile(r"[\w]+(?:-[\w]+)*", re.UNICODE)


def flatten(value):
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(filter(None, (flatten(item) for item in value)))
    return str(value)


def nested_value(record, path):
    value = record.get(path[0])
    if isinstance(value, dict):
        value = value.get(path[1])
    else:
        value = getattr(value, path[1], None) if value is not None else None
    return flatten(value)


def record_fields(record):
    fields = []
    for name in SIMPLE_CONTENT_FIELDS:
        text = normalize_text(flatten(record.get(name)))
        if text:
            fields.append((name, text))
    for path in NESTED_CONTENT_FIELDS:
        text = normalize_text(nested_value(record, path))
        if text:
            fields.append((".".join(path), text))
    return fields


@dataclass(frozen=True)
class ObservedMatch:
    term: Term
    form: str
    fields: Tuple[str, ...]
    museum_only: bool = False
    negated: bool = False


@dataclass
class MatchResult:
    decision: str
    confidence: str
    strength: str
    reasons: List[str]
    matches: List[ObservedMatch]
    negated: List[ObservedMatch]

    def metadata(self):
        matches = self.matches
        return {
            "armenia_decision": self.decision,
            "armenia_confidence": self.confidence,
            "armenia_match_strength": self.strength,
            "armenia_matched_entities": sorted({match.term.entity_id for match in matches}),
            "armenia_matched_terms": sorted({"{}:{}".format(match.term.lang, match.term.value) for match in matches}),
            "armenia_matched_forms": sorted({match.form for match in matches}),
            "armenia_matched_fields": sorted({field for match in matches for field in match.fields}),
            "armenia_match_reasons": sorted(self.reasons),
            "armenia_negated_terms": sorted({"{}:{}".format(match.term.lang, match.term.value) for match in self.negated}),
        }


def split_alternatives(pattern):
    parts = []
    start = 0
    depth = 0
    in_class = False
    escaped = False
    for index, char in enumerate(pattern):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "[":
            in_class = True
        elif char == "]":
            in_class = False
        elif not in_class and char == "(":
            depth += 1
        elif not in_class and char == ")":
            depth -= 1
        elif not in_class and depth == 0 and char == "|":
            parts.append(pattern[start:index])
            start = index + 1
    parts.append(pattern[start:])
    return parts


def literal_prefix(pattern):
    prefix = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            if index + 1 >= len(pattern):
                break
            escaped = pattern[index + 1]
            if escaped.isalnum():
                break
            prefix.append(escaped)
            index += 2
            continue
        if char in ".[(":
            break
        if char in "*+?{":
            if prefix:
                prefix.pop()
            break
        prefix.append(char)
        index += 1
    return "".join(prefix).strip()


class AnchorIndex:
    def __init__(self):
        self.nodes = [{"next": {}, "fail": 0, "outputs": []}]

    def add(self, anchor, term_index):
        state = 0
        for char in anchor:
            child = self.nodes[state]["next"].get(char)
            if child is None:
                child = len(self.nodes)
                self.nodes[state]["next"][char] = child
                self.nodes.append({"next": {}, "fail": 0, "outputs": []})
            state = child
        self.nodes[state]["outputs"].append(term_index)

    def build(self):
        queue = deque()
        for child in self.nodes[0]["next"].values():
            queue.append(child)
        while queue:
            state = queue.popleft()
            for char, child in self.nodes[state]["next"].items():
                queue.append(child)
                failure = self.nodes[state]["fail"]
                while failure and char not in self.nodes[failure]["next"]:
                    failure = self.nodes[failure]["fail"]
                self.nodes[child]["fail"] = self.nodes[failure]["next"].get(char, 0)
                inherited = self.nodes[self.nodes[child]["fail"]]["outputs"]
                self.nodes[child]["outputs"].extend(inherited)

    def find(self, text):
        found = set()
        state = 0
        for char in text:
            while state and char not in self.nodes[state]["next"]:
                state = self.nodes[state]["fail"]
            state = self.nodes[state]["next"].get(char, 0)
            found.update(self.nodes[state]["outputs"])
        return found


class ArmeniaMatcher:
    def __init__(self, terms: Sequence[Term]):
        self.terms = [term for term in terms if term.active]
        self.compiled = []
        self.fallback_terms = set()
        anchors = AnchorIndex()
        for index, term in enumerate(self.terms):
            self.compiled.append(re.compile(r"(?<!\w)(?:{})(?!\w)".format(term.matching_pattern)))
            if term.pattern:
                term_anchors = {literal_prefix(part) for part in split_alternatives(term.matching_pattern)}
            else:
                term_anchors = {normalize_text(term.value)}
            term_anchors = {anchor for anchor in term_anchors if len(anchor) >= 2}
            if not term_anchors:
                self.fallback_terms.add(index)
            for anchor in term_anchors:
                anchors.add(anchor, index)
        anchors.build()
        self.anchors = anchors
        alternatives = "|".join("(?:{})".format(term.matching_pattern) for term in self.terms)
        self.prefilter_regex = r"(?:^|[^\p{L}\p{N}_])(" + alternatives + r")(?:$|[^\p{L}\p{N}_])"
        self.negatives = {
            term.entity_id: re.compile(normalize_text(term.negative_pattern))
            for term in self.terms if term.negative_pattern
        }
        self.weak_terms: Dict[str, List[Term]] = {}
        for term in terms:
            if term.review_status != "rejected" and term.match_strength == "weak" and " " not in normalize_text(term.value):
                self.weak_terms.setdefault(normalize_text(term.value), []).append(term)

    def _observations(self, text, fields, museum_only=False, candidate_hints=None):
        if not text or not self.compiled:
            return [], []
        matches = []
        negated = []
        hint_text = " ".join(candidate_hints) if candidate_hints is not None else text
        candidates = self.anchors.find(hint_text) | self.fallback_terms
        for index in sorted(candidates):
            term = self.terms[index]
            for found in self.compiled[index].finditer(text):
                form = found.group(0)
                matched_fields = tuple(name for name, field_text in fields if form in field_text)
                if museum_only:
                    matched_fields = ("museum.name",)
                if not matched_fields:
                    continue
                observation = ObservedMatch(term, form, matched_fields, museum_only)
                negative = self.negatives.get(term.entity_id)
                if negative and negative.search(text):
                    negated.append(observation)
                else:
                    matches.append(observation)
        return matches, negated

    def _weak_observations(self, fields):
        observations = []
        for field_name, text in fields:
            for token in set(TOKEN_RE.findall(text)):
                for term in self.weak_terms.get(token, []):
                    observations.append(ObservedMatch(term, token, (field_name,)))
        return observations

    def classify(self, record, prefilter_forms=None):
        fields = record_fields(record)
        content_text = " | ".join(text for _, text in fields)
        content_matches, negated = self._observations(content_text, fields, candidate_hints=prefilter_forms)
        museum_text = normalize_text(nested_value(record, MUSEUM_FIELD))
        museum_matches, museum_negated = self._observations(museum_text, (("museum.name", museum_text),), True, prefilter_forms)
        negated.extend(museum_negated)
        weak_matches = self._weak_observations(fields)
        strong = [match for match in content_matches if match.term.match_strength == "strong"]
        context = [match for match in content_matches if match.term.match_strength == "context_only"]
        matches = content_matches + museum_matches + weak_matches
        reasons = []
        if strong:
            decision, confidence, strength = "include", "high", "strong"
            reasons.append("strong_content")
        elif context:
            decision, confidence, strength = "review", "review", "context_only"
            reasons.append("context_only_unconfirmed")
        elif weak_matches:
            decision, confidence, strength = "review", "review", "weak"
            reasons.append("weak_only")
        elif museum_matches:
            decision, confidence, strength = "review", "review", "museum_only"
            reasons.append("museum_only")
        else:
            decision, confidence, strength = "exclude", "excluded", "none"
        if weak_matches and strong:
            reasons.append("weak_support")
        if museum_matches and content_matches:
            reasons.append("museum_support")
        if negated:
            reasons.append("negative_context")
        if not reasons:
            reasons.append("no_active_match")
        return MatchResult(decision, confidence, strength, reasons, matches, negated)

    def count_observations(self, result):
        entities = Counter(match.term.entity_id for match in result.matches)
        fields = Counter(field for match in result.matches for field in match.fields)
        return entities, fields
