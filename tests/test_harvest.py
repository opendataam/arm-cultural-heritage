import harvest_bina
import harvest_iarm
import harvest_wikidata
from harvest_common import Annotator

IARM_TSV = (
    "ID\tCat. Number\tLocation\tCountry\tTown\tPermalink\tDigital Library\tSupport\tDate\tPages\tSize\tTitle\tNote\tGenre\tIIIF Manifest\n"
    "MAF50\t50\tMusée Arménien de France - IRHT\tFrance\tParis\thttps://arca.irht.cnrs.fr/ark:/63955/md24wh249n0k\tARCA\tParchment\t1342"
    "\t354 folios\t13 x 9 cm\tLiturgical books (Eastern Christian)\tMs.\tLiturgy\thttps://api.irht.cnrs.fr/ark:/63955/f5lzamu0bfq7/manifest.json\n"
    "\t12\tBzommar\tLebanon\tBzommar\thttps://w3id.org/vhmml/readingRoom/view/1\tHMML\tPaper\t1700-1800\t\t\tHymnal\t\tLiturgy\t\n"
    "\t12\tBzommar\tLebanon\tBzommar\thttps://w3id.org/vhmml/readingRoom/view/2\tHMML\tPaper\t\t\t\tHymnal\t\tLiturgy\t\n"
)

BINA_ITEM = {
    "o:id": 408216,
    "o:title": "Յառաջ = Haratch",
    "o:media": [{"o:id": 1}, {"o:id": 2}],
    "o:item_set": [{"o:id": 408214}],
    "o:modified": {"@value": "2025-09-09T17:00:58+02:00"},
    "thumbnail_display_urls": {"large": "https://omeka-s.bulac.fr/files/large/408216/a.jpg"},
    "dcterms:title": [{"@value": "Յառաջ = Haratch"}, {"@value": "Yaṙaǰ̌ = Haratch"}],
    "dcterms:creator": [{"@id": "https://www.idref.fr/185503101"}],
    "dcterms:date": [{"@value": "1925-08"}],
    "dcterms:description": [{"@value": "2 août - 30 août 1925"}, {"@value": "N°1-13"}],
    "dcterms:subject": [{"@value": "Périodiques arméniens"}],
    "dcterms:language": [{"@id": "http://id.loc.gov/vocabulary/iso639-2/arm"}, {"@id": "http://id.loc.gov/vocabulary/iso639-2/fra"}],
    "dcterms:rights": [{"@value": "Domaine public"}],
    "dcterms:license": [{"@id": "https://creativecommons.org/publicdomain/mark/1.0/deed.fr"}],
    "dcterms:type": [{"@value": "Périodique"}],
    "dcterms:source": [{"@value": "HARATCH_1925-08"}],
    "dcterms:identifier": [{"@value": "ark:/73193/bkwj1c"}],
    "cld:isLocatedAt": [{"@value": "Bibliothèque universitaire des langues et civilisations"}],
    "bibo:uri": [{"@id": "https://www.sudoc.fr/039874303"}],
}


def claim(value, rank="normal"):
    return {"rank": rank, "mainsnak": {"datavalue": {"value": value}}}


WIKIDATA_ENTITY = {
    "id": "Q154775",
    "modified": "2026-10-01T00:00:00Z",
    "labels": {"hy": {"value": "Ծիծեռնակաբերդ"}, "en": {"value": "Tsitsernakaberd"}, "de": {"value": "Zizernakaberd"}},
    "descriptions": {"en": {"value": "memorial complex in Yerevan"}},
    "claims": {
        "P31": [claim({"id": "Q33506"})],
        "P131": [claim({"id": "Q1953"})],
        "P1435": [claim({"id": "Q1"}, "deprecated"), claim({"id": "Q2"})],
        "P625": [claim({"latitude": 40.1855, "longitude": 44.4903})],
        "P18": [claim("Old.jpg"), claim("Memorial.jpg", "preferred")],
        "P571": [claim({"time": "+1967-00-00T00:00:00Z", "precision": 9})],
    },
}


def test_iarm_ids_are_stable_and_unique():
    rows = harvest_iarm.parse(IARM_TSV, "16355337")
    assert [row["id"] for row in rows] == ["maf50", "bzommar-12", "bzommar-12-2"]
    assert rows[0]["iiif_manifest"].endswith("manifest.json")
    assert rows[0]["zenodo_record"] == "16355337"
    fields = harvest_iarm.matcher_fields(rows[0])
    assert fields["museum"]["name"] == "Musée Arménien de France - IRHT Paris France"


def test_bina_item_is_flattened_with_rights_and_links():
    row = harvest_bina.flatten(BINA_ITEM)
    assert row["title"] == ["Յառաջ = Haratch", "Yaṙaǰ̌ = Haratch"]
    assert row["creator"] == []  # bare authority URIs are not names
    assert row["language"] == ["arm", "fra"]
    assert row["license"].startswith("https://creativecommons.org/publicdomain/mark/")
    assert row["iiif_manifest"] == "https://bina.bulac.fr/iiif/3/408216/manifest"
    assert row["item_url"] == "https://bina.bulac.fr/s/bina/item/408216"
    assert row["media_count"] == 2 and row["item_sets"] == ["408214"]


def test_wikidata_claims_ranks_and_dates():
    assert harvest_wikidata.claim_values(WIKIDATA_ENTITY, "P18") == ["Memorial.jpg", "Old.jpg"]
    assert harvest_wikidata.claim_values(WIKIDATA_ENTITY, "P1435") == [{"id": "Q2"}]
    assert harvest_wikidata.year_of({"time": "+1215-00-00T00:00:00Z", "precision": 9}) == "1215"
    assert harvest_wikidata.year_of({"time": "+1210-00-00T00:00:00Z", "precision": 8}) == "1210s"
    assert harvest_wikidata.year_of({"time": "+1300-00-00T00:00:00Z", "precision": 7}) == "13 century"
    assert harvest_wikidata.year_of({"time": "-0800-00-00T00:00:00Z", "precision": 9}) == "800 BC"


def test_wikidata_row_keeps_interface_languages_and_image_rights():
    labels = {"Q33506": {"en": "museum", "hy": "թանգարան"}, "Q1953": {"en": "Yerevan"}, "Q2": {"en": "monument"}}
    rights = {"Memorial.jpg": {"licence": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0", "artist": "X"}}
    row = harvest_wikidata.build_row(WIKIDATA_ENTITY, labels, rights)
    assert row["labels"] == {"hy": "Ծիծեռնակաբերդ", "en": "Tsitsernakaberd"}
    assert row["types"] == [{"id": "Q33506", "labels": {"en": "museum", "hy": "թանգարան"}}]
    assert row["designations"] == [{"id": "Q2", "labels": {"en": "monument"}}]
    assert (row["latitude"], row["longitude"], row["inception"]) == (40.1855, 44.4903, "1967")
    assert (row["image"], row["image_licence"], row["image_artist"]) == ("Memorial.jpg", "CC BY-SA 4.0", "X")


def test_annotator_includes_dedicated_records_and_links_entities():
    annotator = Annotator()
    linked = annotator.annotate({"name": "Gospel Book", "museum": {"name": "Matenadaran Yerevan Armenia"}})
    assert linked["armenia_decision"] == "include"
    assert linked["armenia_confidence"] == "source"
    assert "place.yerevan" in linked["armenia_matched_entities"]
    assert linked["armenia_matched_fields"] == ["museum.name"]
    unlinked = annotator.annotate({"name": "Hymnal"})
    assert unlinked["armenia_decision"] == "include"
    assert unlinked["armenia_match_reasons"] == ["dedicated_source"]
    assert unlinked["armenia_matched_entities"] == []
