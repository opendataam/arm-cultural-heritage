# Armenian Cultural Heritage Data Sources

Version 2.0 · verified 2026-11-02 · supersedes the undated v1 document.

This document describes institutions and online resources that hold materials on the cultural heritage of Armenia and the Armenian people, with their access methods and **terms of use**. The machine-readable version is [`data/sources.csv`](../data/sources.csv); its format is described in [`sources.md`](sources.md). Every figure is dated; figures that could not be re-verified are marked as such.

**How to read the entries.** *Integration* says how a source fits the project: **harvest** — the source is Armenian-focused and all its records can be taken; **filter** — a general collection from which Armenian records are selected with the multilingual matcher, as already done for Goskatalog; **link** — used for enrichment, identifiers or outbound links only; **not a metadata source** — a funder, publisher or research centre kept for completeness. *Priority*: 1 — MVP; 2 — next wave; 3 — needs an agreement, a key or scraping; 4 — reference only or no integration planned. *Status*: integrated, planned, candidate, blocked (a technical or legal obstacle must be removed first) or not applicable.

**Terms of use.** For each source the entry gives the metadata licence, the general status of digital content, whether commercial use is allowed, whether attribution is required and whether automated access is permitted, with a link to the terms page. Where an institution publishes no terms, Armenian (or the relevant national) copyright law applies by default, and records should not be republished without written permission. Bibliographic facts are generally not protected by copyright, but database rights and website terms can still restrict systematic extraction.

**Method.** Sources were checked on 2026-11-02 with read-only requests to websites, APIs, OAI-PMH endpoints and robots.txt files. No registration, API-key signup, cookie acceptance or bot-protection bypass was performed. Sites that block scripts were checked through their documentation, web search or the Internet Archive Wayback Machine; such figures are flagged. Many Russian state sites were unreachable from outside Russia.

## Summary

- 112 sources in 8 sections.
- Integration: 46 harvest, 23 filter, 39 link, 4 not a metadata source.
- Status: 4 integrated, 4 planned, 80 candidate, 20 blocked, 4 not applicable.
- 29 sources publish metadata under an open licence or in the public domain; 48 publish no usable terms.

## Main changes since v1

- **Structure.** Every source now has dated holdings, access methods, terms of use and an integration decision. Duplicate entries were merged: Goskatalog (20.3 and 24.3), National Library of Russia (20.3 and 24.2), AGBU Nubar Library (14 and 22.5), Mekhitarist Congregation Vienna (3 and 9) and the British Library / Endangered Archives Programme (9 and 19).
- **New sources.** About 60 sources were added, among them Wikidata and Wikimedia Commons, DPLA, the Deutsche Digitale Bibliothek, HathiTrust, Internet Archive, the Met, Polona, the Mekhitarists of Venice, the Armenian Patriarchate of Jerusalem, the Catholicosate of Cilicia, New Julfa, the Vatican Library, Walters, Getty, Chester Beatty, the National Gallery and other Armenian museums, the official state monument lists, RAA, the Armenian Radio Archive, Monument Watch, Caucasus Heritage Watch, SALT Research, NAASR, Zoryan, ANI, USC Shoah Foundation and the GeoNames, Getty and Pleiades gazetteers.
- **UNESCO.** Armenia has 8 intangible heritage elements, not 4 (Duduk 2008, Khachkars 2010, David of Sassoun 2012 and Lavash 2014 were missing), and 3 World Heritage properties, not 4: Echmiatsin and Zvartnots are one property. UNESCO's site terms (2026-09-15) ban bots and bulk downloads; the CC BY-SA datasets on data.unesco.org should be used instead.
- **Armenia.** The National Archives' site is armarchive.am, not archives.am. The Matenadaran holds about 23,000 items, not ~17,000, and 11 Mayr Tsutsak volumes are online, not 8. ARAR now has 327,032 objects. NLA's digital resources are organised as Armenian Book, Armenian Press and the Digital Repository, which has an open DSpace REST API. The AUA 'Literary Texts' collections do not exist; the real resource is DIGILIB. Armenia has no open Goskatalog-style museum register.
- **Counts.** Europeana: 'armenian' 7,582 (v1: 7,329), multilingual query 18,393. Project SAVE: 150,000+ photographs, not 100,000+. AGBU Nubar: 800,000 archival documents, not 500,000. Hrant Dink map: 9,727 sites, 4,485 of them Armenian. The LoC figure of 50,000+ Armenian-language items is not supported by LoC sources; Gallica and Trove counts could not be re-verified.
- **Attribution of collections.** The Columbia Armenian Oral History Archive exists (MS#1480, Parsegian, 130–139 interviews). The Hovannisian oral history collection is now held by USC Shoah Foundation, not UCLA. The 64,000-card Armenian catalogue belongs to the National Library of Russia, not Goskatalog. RGIA fund 821 covers all non-Orthodox confessions, and the main Lazarev archive is in RGADA. The German Foreign Office edition is armenocide.net, not Lepsiushaus. Gulbenkian's Armenian Communities Department is in Lisbon. Freer Gallery holdings are now under the National Museum of Asian Art.
- **Platform changes.** The Met retired its v1 search API on 2026-10-01 (replacement v1.1). The NYPL Repo API was withdrawn on 2026-08-01. Chronicling America moved into loc.gov in 2025. The Mazarine digital library moved to the Institut de France platform. Trove's 2025 API terms limit use to descriptive metadata. CyberLeninka's 2025 terms ban automated metadata harvesting.
- **Removed.** 'Various European national libraries' (no identifiable source). Open Data Armenia is no longer evaluated as a source: it is the project's own publication portal (see the appendix).

## Terms of use at a glance

`unknown` means no licence or terms were found; such sources need written permission before their records are republished. Source-level values do not replace item-level rights statements.

| Source | Metadata licence | Content | Commercial | Automated access | Integration | Priority |
| --- | --- | --- | --- | --- | --- | ---: |
| [National Library of Armenia](#national-library-of-armenia) | `unknown` | mixed, per item | no | API only | harvest | 2 |
| [Matenadaran – Mesrop Mashtots Research Institute of Ancient Manuscripts](#matenadaran--mesrop-mashtots-research-institute-of-ancient-manuscripts) | `unknown` | restricted | unknown | allowed | harvest | 3 |
| [Pan-Armenian Digital Library (ARAR)](#pan-armenian-digital-library-arar) | `unknown` | mixed, per item | unknown | API only | harvest | 2 |
| [History Museum of Armenia](#history-museum-of-armenia) | `all-rights-reserved` | all rights reserved | no | allowed | harvest | 3 |
| [Armenian Genocide Museum-Institute](#armenian-genocide-museum-institute) | `all-rights-reserved` | all rights reserved | unknown | allowed | harvest | 3 |
| [National Archives of Armenia](#national-archives-of-armenia) | `unknown` | restricted | unknown | unknown | link | 3 |
| [State Lists of Immovable Historical and Cultural Monuments of the Republic of Armenia](#state-lists-of-immovable-historical-and-cultural-monuments-of-the-republic-of-armenia) | `public-domain` | public domain | yes | unknown | harvest | 2 |
| [Scientific Research Center of Historical and Cultural Heritage](#scientific-research-center-of-historical-and-cultural-heritage) | `unknown` | unknown | unknown | allowed | link | 4 |
| [Electronic Information Database of Cultural Values ('Armenian Treasury')](#electronic-information-database-of-cultural-values-armenian-treasury) | `unknown` | unknown | unknown | unknown | harvest | 3 |
| [Mother See of Holy Etchmiadzin – Vache and Tamar Manoukian Matenadaran (Library)](#mother-see-of-holy-etchmiadzin--vache-and-tamar-manoukian-matenadaran-library) | `all-rights-reserved` | all rights reserved | no | allowed | harvest | 3 |
| [National Gallery of Armenia](#national-gallery-of-armenia) | `unknown` | unknown | unknown | restricted | harvest | 3 |
| [Yeghishe Charents Museum of Literature and Arts (GAT Museum)](#yeghishe-charents-museum-of-literature-and-arts-gat-museum) | `all-rights-reserved` | all rights reserved | unknown | unknown | harvest | 3 |
| [Komitas Museum-Institute](#komitas-museum-institute) | `all-rights-reserved` | mixed, per item | unknown | allowed | harvest | 3 |
| [Sergei Parajanov Museum](#sergei-parajanov-museum) | `all-rights-reserved` | all rights reserved | no | allowed | harvest | 3 |
| [Erebuni Historical and Archaeological Museum-Reserve](#erebuni-historical-and-archaeological-museum-reserve) | `unknown` | unknown | unknown | unknown | link | 4 |
| [Institute of Archaeology and Ethnography, National Academy of Sciences of the Republic of Armenia](#institute-of-archaeology-and-ethnography-national-academy-of-sciences-of-the-republic-of-armenia) | `unknown` | unknown | unknown | allowed | link | 4 |
| [Research on Armenian Architecture (RAA) Foundation](#research-on-armenian-architecture-raa-foundation) | `all-rights-reserved` | all rights reserved | no | allowed | harvest | 3 |
| [Public Radio of Armenia – Armenian Radio Archive](#public-radio-of-armenia--armenian-radio-archive) | `all-rights-reserved` | all rights reserved | no | allowed | harvest | 3 |
| [National Cinema Center of Armenia](#national-cinema-center-of-armenia) | `unknown` | restricted | unknown | unknown | link | 4 |
| [Digital Library of Armenian Literature (DIGILIB)](#digital-library-of-armenian-literature-digilib) | `unknown` | mixed, per item | unknown | allowed | harvest | 3 |
| [American University of Armenia Library – Digital Collections](#american-university-of-armenia-library--digital-collections) | `unknown` | mixed, per item | unknown | allowed | filter | 3 |
| [Eastern Armenian National Corpus (EANC)](#eastern-armenian-national-corpus-eanc) | `unknown` | restricted | unknown | unknown | link | 4 |
| [Index of Digitized Armenian Manuscripts (IArM)](#index-of-digitized-armenian-manuscripts-iarm) | `CC-BY-4.0` | mixed, per item | yes | allowed | harvest | 1 |
| [Mekhitarist Congregation, San Lazzaro degli Armeni (Venice) - Library and Manuscript Catalogue](#mekhitarist-congregation-san-lazzaro-degli-armeni-venice---library-and-manuscript-catalogue) | `CC-BY-NC-4.0` | unknown | no | allowed | harvest | 2 |
| [Mekhitarist Congregation Vienna (Mechitharisten) - Library and Periodicals Portal](#mekhitarist-congregation-vienna-mechitharisten---library-and-periodicals-portal) | `unknown` | unknown | unknown | API only | harvest | 2 |
| [Armenian Patriarchate of Jerusalem (St. James Monastery; manuscript library and Calouste Gulbenkian Library)](#armenian-patriarchate-of-jerusalem-st-james-monastery-manuscript-library-and-calouste-gulbenkian-library) | `unknown` | unknown | unknown | unknown | link | 4 |
| [Catholicosate of the Great House of Cilicia, Antelias (Cilicia Library and Manuscript Center; Cilicia Museum)](#catholicosate-of-the-great-house-of-cilicia-antelias-cilicia-library-and-manuscript-center-cilicia-museum) | `CC-BY-4.0` | restricted | no | restricted | link | 3 |
| [Holy Savior (Vank) Cathedral museum and Nerses Shnorhali Library, New Julfa, Isfahan](#holy-savior-vank-cathedral-museum-and-nerses-shnorhali-library-new-julfa-isfahan) | `unknown` | all rights reserved | unknown | unknown | link | 4 |
| [Korneli Kekelidze Georgian National Centre of Manuscripts (Tbilisi)](#korneli-kekelidze-georgian-national-centre-of-manuscripts-tbilisi) | `all-rights-reserved` | all rights reserved | unknown | allowed | link | 4 |
| [Biblioteca Apostolica Vaticana - DigiVatLib (Vat. arm., Borg. arm. and other fonds)](#biblioteca-apostolica-vaticana---digivatlib-vat-arm-borg-arm-and-other-fonds) | `unknown` | all rights reserved | conditional | restricted | link | 3 |
| [British Library - Armenian manuscripts (Archives and Manuscripts Catalogue / Digitised Manuscripts)](#british-library---armenian-manuscripts-archives-and-manuscripts-catalogue--digitised-manuscripts) | `unknown` | mixed, per item | conditional | allowed | filter | 3 |
| [British Library Endangered Archives Programme (EAP) - Armenian projects](#british-library-endangered-archives-programme-eap---armenian-projects) | `unknown` | restricted | conditional | restricted | harvest | 2 |
| [Bodleian Libraries, University of Oxford (Digital Bodleian) - Armenian Manuscripts and Printed Books](#bodleian-libraries-university-of-oxford-digital-bodleian---armenian-manuscripts-and-printed-books) | `unknown` | restricted | conditional | allowed | harvest | 2 |
| [Chester Beatty (Dublin) - Armenian manuscripts](#chester-beatty-dublin---armenian-manuscripts) | `unknown` | open licences | yes | restricted | harvest | 3 |
| [Bayerische Staatsbibliothek - Digitale Sammlungen / MDZ (Cod.armen.)](#bayerische-staatsbibliothek---digitale-sammlungen--mdz-codarmen) | `unknown` | public domain | yes | allowed | harvest | 2 |
| [Real Biblioteca del Monasterio de San Lorenzo de El Escorial - Real Biblioteca Digital](#real-biblioteca-del-monasterio-de-san-lorenzo-de-el-escorial---real-biblioteca-digital) | `unknown` | unknown | unknown | allowed | none | 4 |
| [Musée Arménien de France (Fondation Nourhan Fringhian), Paris](#musée-arménien-de-france-fondation-nourhan-fringhian-paris) | `unknown` | restricted | no | unknown | harvest | 2 |
| [Biblissima+ (portal, IIIF Collections of Manuscripts and Rare Books, data.biblissima.fr)](#biblissima-portal-iiif-collections-of-manuscripts-and-rare-books-databiblissimafr) | `etalab-2.0` | mixed, per item | conditional | restricted | link | 3 |
| [Walters Art Museum - Armenian manuscripts (Digital Walters)](#walters-art-museum---armenian-manuscripts-digital-walters) | `CC0-1.0` | open licences | yes | allowed | harvest | 2 |
| [J. Paul Getty Museum - Armenian manuscripts](#j-paul-getty-museum---armenian-manuscripts) | `CC0-1.0` | open licences | yes | allowed | harvest | 2 |
| [OPenn (University of Pennsylvania Libraries), incl. Free Library of Philadelphia and Walters mirror](#openn-university-of-pennsylvania-libraries-incl-free-library-of-philadelphia-and-walters-mirror) | `CC-BY-4.0` | public domain | yes | allowed | link | 4 |
| [Hill Museum & Manuscript Library (HMML) - vHMML / HMML Reading Room](#hill-museum--manuscript-library-hmml---vhmml--hmml-reading-room) | `CC-BY-4.0` | restricted | no | restricted | harvest | 2 |
| [Bibliothèque Orientale, Université Saint-Joseph (Beirut)](#bibliothèque-orientale-université-saint-joseph-beirut) | `CC-BY-4.0` | restricted | no | restricted | link | 4 |
| [Europeana](#europeana) | `CC0-1.0` | mixed, per item | conditional | API only | filter | 1 |
| [German Digital Library](#german-digital-library) | `CC0-1.0` | mixed, per item | conditional | API only | filter | 2 |
| [Gallica (Bibliothèque nationale de France)](#gallica-bibliothèque-nationale-de-france) | `etalab-2.0` | mixed, per item | conditional | restricted | filter | 2 |
| [BULAC (University Library of Languages and Civilizations)](#bulac-university-library-of-languages-and-civilizations) | `etalab-2.0` | mixed, per item | conditional | unknown | harvest | 1 |
| [Bibliothèque Mazarine](#bibliothèque-mazarine) | `custom` | restricted | conditional | allowed | link | 4 |
| [FranceArchives](#francearchives) | `etalab-2.0` | mixed, per item | conditional | restricted | filter | 3 |
| [Hispana](#hispana) | `unknown` | mixed, per item | unknown | unknown | link | 4 |
| [Polona](#polona) | `unknown` | mixed, per item | conditional | unknown | filter | 3 |
| [Library of Congress](#library-of-congress) | `public-domain` | mixed, per item | conditional | restricted | filter | 2 |
| [Digital Public Library of America](#digital-public-library-of-america) | `CC0-1.0` | mixed, per item | conditional | API only | filter | 2 |
| [HathiTrust Digital Library](#hathitrust-digital-library) | `CC0-1.0` | mixed, per item | conditional | restricted | filter | 2 |
| [Internet Archive](#internet-archive) | `unknown` | mixed, per item | conditional | API only | filter | 2 |
| [Smithsonian Open Access](#smithsonian-open-access) | `CC0-1.0` | mixed, per item | conditional | allowed | filter | 2 |
| [The Metropolitan Museum of Art Open Access](#the-metropolitan-museum-of-art-open-access) | `CC0-1.0` | mixed, per item | conditional | allowed | filter | 2 |
| [NYPL Digital Collections](#nypl-digital-collections) | `unknown` | mixed, per item | conditional | restricted | filter | 4 |
| [Trove](#trove) | `custom` | mixed, per item | conditional | restricted | filter | 3 |
| [State Catalogue of the Museum Fund of the Russian Federation](#state-catalogue-of-the-museum-fund-of-the-russian-federation) | `custom` | restricted | yes | restricted | filter | 1 |
| [Institute of Oriental Manuscripts, Russian Academy of Sciences (IOM RAS), St Petersburg](#institute-of-oriental-manuscripts-russian-academy-of-sciences-iom-ras-st-petersburg) | `unknown` | unknown | unknown | unknown | link | 4 |
| [National Library of Russia](#national-library-of-russia) | `custom` | restricted | no | restricted | link | 4 |
| [Russian State Library](#russian-state-library) | `custom` | mixed, per item | unknown | unknown | filter | 3 |
| [National Electronic Library (NEB)](#national-electronic-library-neb) | `custom` | mixed, per item | no | prohibited | filter | 4 |
| [Presidential Library named after B. N. Yeltsin](#presidential-library-named-after-b-n-yeltsin) | `all-rights-reserved` | mixed, per item | unknown | unknown | filter | 4 |
| [State Hermitage Museum](#state-hermitage-museum) | `all-rights-reserved` | all rights reserved | no | unknown | link | 4 |
| [Russian Museum of Ethnography](#russian-museum-of-ethnography) | `custom` | restricted | no | restricted | link | 4 |
| [Armenian Museum of Moscow and Culture of Nations](#armenian-museum-of-moscow-and-culture-of-nations) | `all-rights-reserved` | all rights reserved | no | restricted | link | 4 |
| [Russian State Historical Archive](#russian-state-historical-archive) | `unknown` | restricted | unknown | unknown | link | 4 |
| [Russian State Archive of Ancient Acts](#russian-state-archive-of-ancient-acts) | `unknown` | restricted | unknown | unknown | link | 4 |
| [Russian State Military Historical Archive](#russian-state-military-historical-archive) | `unknown` | restricted | unknown | unknown | link | 4 |
| [CyberLeninka](#cyberleninka) | `custom` | mixed, per item | no | prohibited | filter | 4 |
| [eLIBRARY.RU Scientific Electronic Library](#elibraryru-scientific-electronic-library) | `unknown` | mixed, per item | unknown | restricted | filter | 4 |
| [Runivers](#runivers) | `all-rights-reserved` | restricted | no | restricted | link | 4 |
| [Electronic Library of Historical Documents (EBID), Russian Historical Society](#electronic-library-of-historical-documents-ebid-russian-historical-society) | `unknown` | unknown | unknown | unknown | link | 4 |
| [Houshamadyan – Open Digital Archive (ODA)](#houshamadyan--open-digital-archive-oda) | `all-rights-reserved` | all rights reserved | no | unknown | harvest | 3 |
| [AGBU Nubar Library](#agbu-nubar-library) | `all-rights-reserved` | all rights reserved | no | unknown | harvest | 3 |
| [ARAM – Association for Research and Archiving of Armenian Memory](#aram--association-for-research-and-archiving-of-armenian-memory) | `unknown` | unknown | unknown | allowed | harvest | 3 |
| [OFPRA Archives – Armenian refugee files (Nansen-era protection records)](#ofpra-archives--armenian-refugee-files-nansen-era-protection-records) | `unknown` | restricted | no | restricted | link | 4 |
| [Gomidas Institute](#gomidas-institute) | `all-rights-reserved` | all rights reserved | no | allowed | none | 4 |
| [SALT Research](#salt-research) | `unknown` | mixed, per item | no | restricted | filter | 3 |
| [Haigazian University – Armenian Diaspora Research Center (ADRC)](#haigazian-university--armenian-diaspora-research-center-adrc) | `unknown` | unknown | unknown | allowed | harvest | 3 |
| [Foundation for Culture and Heritage of Polish Armenians](#foundation-for-culture-and-heritage-of-polish-armenians) | `CC-BY-SA-3.0` | mixed, per item | conditional | unknown | harvest | 3 |
| [Lepsiushaus Potsdam](#lepsiushaus-potsdam) | `all-rights-reserved` | restricted | no | unknown | link | 4 |
| [Calouste Gulbenkian Foundation – Armenian Communities Department](#calouste-gulbenkian-foundation--armenian-communities-department) | `all-rights-reserved` | all rights reserved | no | unknown | none | 4 |
| [Diario Armenia](#diario-armenia) | `custom` | all rights reserved | conditional | unknown | link | 4 |
| [Centre for Armenian Studies, National University of Rosario (Cátedra Armenia)](#centre-for-armenian-studies-national-university-of-rosario-cátedra-armenia) | `unknown` | unknown | unknown | unknown | none | 4 |
| [Armenian Museum of America](#armenian-museum-of-america) | `all-rights-reserved` | all rights reserved | no | prohibited | harvest | 3 |
| [Project SAVE Armenian Photograph Archives (Project Save Photograph Archive)](#project-save-armenian-photograph-archives-project-save-photograph-archive) | `custom` | all rights reserved | conditional | restricted | harvest | 3 |
| [NAASR Edward and Helen Mardigian Library (National Association for Armenian Studies and Research)](#naasr-edward-and-helen-mardigian-library-national-association-for-armenian-studies-and-research) | `unknown` | unknown | unknown | unknown | harvest | 3 |
| [Krikor and Clara Zohrab Information Center](#krikor-and-clara-zohrab-information-center) | `unknown` | unknown | unknown | restricted | harvest | 3 |
| [USC Dornsife Institute of Armenian Studies](#usc-dornsife-institute-of-armenian-studies) | `unknown` | mixed, per item | conditional | restricted | harvest | 3 |
| [USC Shoah Foundation Visual History Archive](#usc-shoah-foundation-visual-history-archive) | `all-rights-reserved` | restricted | no | prohibited | link | 4 |
| [Richard G. Hovannisian Armenian Genocide Oral History Collection (formerly UCLA Armenian Genocide Oral History Project)](#richard-g-hovannisian-armenian-genocide-oral-history-collection-formerly-ucla-armenian-genocide-oral-history-project) | `all-rights-reserved` | restricted | no | prohibited | link | 4 |
| [Columbia Armenian Oral History Archive, 1968-1977 (Oral History Archives at Columbia, Rare Book & Manuscript Library)](#columbia-armenian-oral-history-archive-1968-1977-oral-history-archives-at-columbia-rare-book--manuscript-library) | `unknown` | mixed, per item | conditional | restricted | harvest | 3 |
| [Zoryan Institute](#zoryan-institute) | `unknown` | restricted | conditional | unknown | link | 4 |
| [Armenian National Institute](#armenian-national-institute) | `all-rights-reserved` | all rights reserved | no | restricted | harvest | 3 |
| [Rockefeller Archive Center - Near East Foundation records (Near East Relief)](#rockefeller-archive-center---near-east-foundation-records-near-east-relief) | `CC0-1.0` | mixed, per item | conditional | allowed | filter | 2 |
| [Armenian Studies Program, California State University, Fresno](#armenian-studies-program-california-state-university-fresno) | `unknown` | mixed, per item | conditional | allowed | harvest | 2 |
| [Hairenik Association - Hairenik Digital Archives (Hairenik / Armenian Weekly)](#hairenik-association---hairenik-digital-archives-hairenik--armenian-weekly) | `unknown` | restricted | conditional | unknown | link | 4 |
| [The Armenian Mirror-Spectator](#the-armenian-mirror-spectator) | `all-rights-reserved` | all rights reserved | no | restricted | link | 4 |
| [UNESCO Intangible Cultural Heritage](#unesco-intangible-cultural-heritage) | `CC-BY-SA-4.0` | mixed, per item | conditional | API only | harvest | 2 |
| [UNESCO World Heritage Centre](#unesco-world-heritage-centre) | `CC-BY-SA-4.0` | mixed, per item | conditional | API only | harvest | 2 |
| [Hrant Dink Foundation – Turkey Cultural Heritage Map](#hrant-dink-foundation--turkey-cultural-heritage-map) | `unknown` | unknown | unknown | unknown | harvest | 2 |
| [Monument Watch – Monitoring the Cultural Heritage of Artsakh](#monument-watch--monitoring-the-cultural-heritage-of-artsakh) | `all-rights-reserved` | all rights reserved | unknown | unknown | harvest | 3 |
| [Caucasus Heritage Watch](#caucasus-heritage-watch) | `unknown` | all rights reserved | unknown | unknown | harvest | 3 |
| [Wikidata](#wikidata) | `CC0-1.0` | open licences | yes | allowed | harvest | 1 |
| [Wikimedia Commons](#wikimedia-commons) | `CC-BY-SA-4.0` | open licences | yes | allowed | link | 2 |
| [GeoNames](#geonames) | `CC-BY-4.0` | open licences | yes | allowed | link | 2 |
| [Getty Vocabularies (AAT, TGN, ULAN)](#getty-vocabularies-aat-tgn-ulan) | `ODC-By-1.0` | open licences | yes | allowed | link | 4 |
| [Pleiades](#pleiades) | `CC-BY-3.0` | open licences | yes | restricted | link | 4 |
| [VIAF: The Virtual International Authority File](#viaf-the-virtual-international-authority-file) | `ODC-By-1.0` | open licences | yes | restricted | link | 4 |

## 1. Armenia

National institutions, museums and digital libraries in Armenia. None of them publishes an open licence; harvesting requires written permission even where machine access is open.

### National Library of Armenia

*Հայաստանի ազգային գրադարան* · <https://nla.am> · AM · library · `am.nla`

World's largest repository of Armenian printed heritage and the centre of the national bibliography. Its digital resources are now organised as three main databases: **Armenian Book** (haygirk.nla.am, books 1512–1940, including the 1512–1800 rare-book section; 211 titles were digitised under British Library EAP180), **Armenian Press** (tert.nla.am, periodicals from 1794 to the present) and the **Digital Repository** (dspace.nla.am: theses, NLA publications, Armenica, Endangered Heritage of Artsakh). The older thematic databases (Maps, Amulets, The Bible, Printing Houses, Armenians in the Great Patriotic War, anniversaries of the Armenian book) remain reachable from nla.am. Related services: union catalogue ArmUniCat (armunicat.nla.am) and journal.nla.am.

- **Holdings:** 13,244 items in the NLA DSpace digital repository (api.nla.am discover/search, dsoType=ITEM), queried 2026-11-02. Excludes the separate Armenian Book (haygirk.nla.am) and Armenian Press (tert.nla.am) databases, whose sizes could not be read (Cloudflare).
- **Access:** API, web pages (no authentication); endpoint <https://api.nla.am/server/api>; metadata: json, dc.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use no; attribution required; automated access API only. The Armenian Book database states that its materials may be used for personal, academic and informational purposes, with a mandatory reference to the NLA databases; commercial use is not granted. No licence is published for the DSpace repository (items carry no dc.rights), so Armenian Law on Copyright and Related Rights (2006) applies by default; theses and recent NLA publications are in copyright. [Terms](https://haygirk.nla.am)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Digital Repository runs DSpace 9.2 (not 7); REST API at https://api.nla.am/server/api is open and unauthenticated. One top community ('Digital Repository of NLA') with 6 sub-communities: Theses & Abstracts; Endangered Heritage of Artsakh; NLA Publications; Armenica; International mass media about Artsakh; Non-Book Publications. The DSpace OAI endpoint https://api.nla.am/server/oai/request returns HTTP 500 (2026-11-02). The UI (dspace.nla.am), nla.am, haygirk and tert are behind a Cloudflare managed challenge, so harvest through the REST API only. Platform of haygirk/tert unknown. Related: union catalogue armunicat.nla.am, journal.nla.am (OJS).

### Matenadaran – Mesrop Mashtots Research Institute of Ancient Manuscripts

*Մեսրոպ Մաշտոցի անվան հին ձեռագրերի գիտահետազոտական ինստիտուտ – Մատենադարան* · <https://matenadaran.am> · AM · research institute · `am.matenadaran`

Mesrop Mashtots Research Institute of Ancient Manuscripts: about 23,000 manuscripts, fragments and amulets in all languages, of which 11,230 basic Armenian manuscripts, 2,200 fragments and 530 scrolls. About 8,000 Armenian manuscripts have been digitised since 2007, but there is no public item-level viewer. The **Mayr Tsutsak** (Main Catalogue) is published as PDFs of 11 volumes (40 projected), alongside the short catalogue, the Catholicosal Diwan catalogue, *Matenagirk Hayots* and the journals *Banber Matenadarani* and *MEMAS*. The 30-point description scheme goes back to Fr. Hakovbos Tashian (Vienna Mekhitarists, 1890s). A Gulbenkian-funded catalogue access platform was announced for July 2026 but had not launched by November 2026.

- **Holdings:** Armenian holdings: 11,230 basic manuscripts + 2,200 fragments + 530 scrolls (Mayr Tsutsak page, matenadaran.am, read 2026-11-02). The repository page gives ~23,000 manuscripts, fragments and amulets in all languages. None of these are browsable as item-level records online.
- **Access:** web pages (no authentication); metadata: html, other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access allowed. No reuse or licensing terms are published. Digital copies of manuscripts are supplied for a fee under a price list (linked). Armenian Law on Copyright and Related Rights (2006) applies by default; the medieval texts are public domain, but image reuse needs the institute's permission. robots.txt blocks only /wp-admin/. [Terms](https://matenadaran.am/%d5%b4%d5%a1%d5%bf%d5%a5%d5%b6%d5%a1%d5%a4%d5%a1%d6%80%d5%a1%d5%b6/%d5%ae%d5%a1%d5%bc%d5%a1%d5%b5%d5%b8%d6%82%d5%a9%d5%b5%d5%b8%d6%82%d5%b6%d5%b6%d5%a5%d6%80/%d5%a9%d5%be%d5%a1%d5%b5%d5%ab%d5%b6-%d5%ba%d5%a1%d5%bf%d5%b3%d5%a5%d5%b6%d5%b6%d5%a5%d6%80%d5%ab-%d5%a3%d5%b6%d5%a1%d6%81%d5%b8%d6%82%d6%81%d5%a1%d5%af/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** WordPress; the public wp-json REST API works (posts/pages search) and wp-sitemap.xml is available. The 'Digital repositories' menu lists: Digital library (publication PDFs under /ftp/el_gradaran/), Mayr Tsutsak PDFs (/ftp/data/M/Hator-N.pdf), Catholicosal Diwan catalogue, Matenagirk Hayots (medieval texts), early printed books, maps, Banber Matenadarani (banber.matenadaran.am) and MEMAS (journalmatenadaran.com). No IIIF or image viewer. Manuscript records overlap with the Index of Armenian Manuscripts and the Mayr Tsutsak PDFs.

### Pan-Armenian Digital Library (ARAR)

*Համահայկական թուանշային գրադարան* · <https://arar.sci.am> · AM · digital library · `am.arar`

Pan-Armenian Digital Library run by the Fundamental Scientific Library of NAS RA on dLibra. It holds books, articles, periodicals, the Mekhitarist Congregation Vienna periodicals portal and its collection of Armenian and Armeno-Turkish publications, publications of NAS RA institutes (Arts, Oriental Studies, Geological Sciences, Literature, Archaeology and Ethnography), the Digital Repatriation project, an audio archive, maps, posters and exhibitions. Partners include the History Museum of Armenia, the National Agrarian University and Grigor Narekatsi University (Stepanakert).

- **Holdings:** Homepage counter: 'contains 327 032 digital objects' (2026-11-02). OAI-PMH ListIdentifiers (oai_dc) reports completeListSize=309,205 on the same date. Mostly Armenian-language or Armenia-related, but includes NAS RA science publications.
- **Access:** OAI-PMH, web pages (no authentication); endpoint <https://arar.sci.am/oai-pmh-repository.xml>; metadata: dc, qdc, mets, other.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use unknown; attribution unknown; automated access API only. No terms of use or licence page exists (the dLibra 'polityka' page is undefined). The OAI records carry no dc:rights, and the Rights/License/Access-rights fields shown on item pages are empty. Some items are restricted to privileged accounts. The 'About' page states an open-science mission only, so Armenian Law on Copyright and Related Rights (2006) applies by default.
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** dLibra 6.2.12 (PSNC Poznań). OAI formats: oai_dc, oai_qdc, mets, dlibra_avs, oai_etdms. Sets include books1, Articles, periodicals1, Mekhitaristcongregation(+books), armenian_and_armenogram_turkish_publications, institute_of_arts, pubios, IGS, InstLit, IAE, digital (repatriation), Audio, Maps, Posters, exhibition. robots.txt disallows /Content/*/download*, zip and search-result pages, so harvest metadata over OAI and avoid bulk file download. No IIIF manifest found. Hosts digitized Etchmiadzin journal (publication 369886) and IAE publications (set IAE, 580 records).

### History Museum of Armenia

*Հայաստանի պատմության թանգարան* · <https://historymuseum.am> · AM · museum · `am.history-museum`

National museum with about 400,000 objects (archaeology, numismatics, ethnography, documents). The online collection is a curated selection of about 600 records, mostly photo and archive fonds, in Armenian only. The museum took part in the *Treasures of Artsakh* virtual exhibition. The CDLI partnership mentioned in v1 was not confirmed.

- **Holdings:** 599 records in wp-sitemap-posts-collections_type-1.xml (online collection; about 50 pages × 12), 2026-11-02. The museum holds about 400,000 objects in total (homepage).
- **Access:** web pages (no authentication); endpoint <https://historymuseum.am/wp-sitemap-posts-collections_type-1.xml>; metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. Photos on the site are protected under Armenian copyright law. Reproducing, distributing, adapting or otherwise reusing them is prohibited without the museum's prior permission. Site copyright is reserved (the footer year is an unfilled placeholder). [Terms](https://historymuseum.am/terms-and-conditions/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** WordPress; the REST API is closed to anonymous users ('Only authenticated users can access the REST API'). robots.txt blocks only /wp-admin/; records are reachable via the sitemap and taxonomy filters (collection_filter, period_filter, location_filter, material_filter). Records are Armenian-language only.

### Armenian Genocide Museum-Institute

*Հայոց ցեղասպանության թանգարան-ինստիտուտ* · <https://www.genocide-museum.am/eng/> · AM · museum · `am.agmi`

Museum and research institute of the Armenian Genocide. The website offers curated static pages in four languages: the photo collection, online exhibitions, 100 photographic stories, mapping, cultural genocide, survivor stories and document selections grouped by country of origin (American, British, German, Russian, French, Austrian, Turkish). The collection was reported at about 90,000 documents in 2015; there is no searchable database.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use unknown; attribution unknown; automated access allowed. No terms of use or photo-reuse policy is published; the only notice is a generic footer copyright line ('2007-2021 © The Armenian Genocide Museum-Institute'). Armenian Law on Copyright and Related Rights (2006) applies by default; many pre-1923 photos may be public domain, but AGMI gives no rights statements. [Terms](https://www.genocide-museum.am/eng/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Plain PHP site in four languages (Eng/Հայ/Türk/Рус); robots.txt is empty. No API. Its USC Shoah Foundation VHA testimonies are licensed third-party content.

### National Archives of Armenia

*Հայաստանի ազգային արխիվ* · <https://armarchive.am> · AM · archive · `am.national-archives`

State archive with about 5,800 fonds and 3.4 million storage units, including the archives of the Holy Synod of Etchmiadzin and the National Film Library. **Correction:** the official site is armarchive.am; archives.am (listed in v1) is an unrelated site, and the old armarchives.am domain now hosts a betting site. armarchive.am timed out from outside Armenia on 2026-11-02.

- **Access:** web pages (restricted / by agreement); metadata: html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. No online terms could be read (site unreachable). Per EHRI, reading-room access requires an official letter from the researcher's institution addressed to the Director General. Archival documents fall under the Law on Archives and copyright law defaults. [Terms](https://portal.ehri-project.eu/countries/am)
- **Integration:** link / enrich only; priority 3; blocked.
- **Notes:** Services reported: reading hall, online exhibitions, e-requests, genealogy service. The film archive (National Film Library / Cine-Photo Documentation branch) is part of the National Archives and holds most Hayfilm output. Retry armarchive.am from an Armenian network or by hand.

### State Lists of Immovable Historical and Cultural Monuments of the Republic of Armenia

*Պատմության և մշակույթի անշարժ հուշարձանների պետական ցուցակ* · <https://www.arlis.am> · AM · registry · `am.monuments-state-list`

The legal register of immovable historical and cultural monuments: Government decisions approving lists per marz and for Yerevan (2002–2004) with later amendments, about 24,000 entries with state index codes. The texts are published on ARLIS; no official machine-readable dataset exists. Wiki Loves Monuments Armenia and Wikidata reuse the state index codes.

- **Holdings:** 24,221 immovable monuments on the state lists per 2019 data reported in the press (hyetert.org, 19 Sep 2020; other reports date the figure to 2021). This counts list entries, not digital records.
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `public-domain`; content public domain; commercial use yes; attribution not required; automated access unknown. The lists are Government decisions, which are legal acts. Article 4 of the Law on Copyright and Related Rights excludes official documents (legal acts, treaties and their official translations) from copyright, so the list texts are free to reuse. ARLIS publishes no separate site terms. [Terms](https://en.wikisource.org/wiki/Armenia._Law_on_Copyright_and_Related_Rights)
- **Integration:** harvest all records; priority 2; planned.
- **Notes:** Legal basis: Law on the Protection and Use of Immovable Monuments of History and Culture and of Historical Environment (1998). Entries carry state index codes (պետցուցիչ, e.g. 3.82.1). The lists exist only as tables inside decision texts on ARLIS; the new ARLIS uses URLs like /hy/acts/{id}/latest, and amendments must be merged. No official machine-readable dataset was found; escs.am returns HTTP 403 (Cloudflare) to scripts. Overlaps: Wiki Loves Monuments Armenia lists and Wikidata use these codes.

### Scientific Research Center of Historical and Cultural Heritage

*«Պատմամշակութային ժառանգության գիտահետազոտական կենտրոն» ՊՈԱԿ* · <https://armheritage.am> · AM · research institute · `am.armheritage`

State research centre (SNCO of the Ministry of ESCS, successor of the *Corpus of Armenian Monuments* editorial office since 2003). It prepares documentation for the state monument lists and publishes the *Divan of Armenian Monuments* series, the journal *Hushardzan* and archaeological reports. The website publishes articles; no structured monument database is online.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access allowed. No terms or copyright statement is published; the footer only credits the web developer. Armenian Law on Copyright and Related Rights (2006) applies by default. robots.txt blocks only /wp-admin/.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** WordPress (wp-sitemap.xml available). An English version exists at /en/home/. Useful for monument descriptions, but there is no structured register here; the legal register is the Government-approved state lists (see am.monuments-state-list).

### Electronic Information Database of Cultural Values ('Armenian Treasury')

<https://treasury.am> · AM · registry · `am.museum-register`

Electronic Information Database of Cultural Values (Government decision N 1058-Ն, 2014): about 156,600 approved records from 41 organisations by 2020. It is the nearest Armenian equivalent of Russia's Goskatalog, but it is not public or open, and its current address (possibly treasury.am) could not be confirmed.

- **Holdings:** About 156,586 cultural values entered and approved, from 41 state and community organisations (Compendium of Cultural Policies, Armenia profile 2.4; figure from ~2020, when the first stage ended).
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No terms could be found. The live site could not be inspected; treasury.am returns a Cloudflare challenge, and it is not confirmed that this domain hosts the database. Armenian Law on Copyright and Related Rights (2006) applies by default. [Terms](https://www.culturalpolicies.net/country_profile/armenia-2-4)
- **Integration:** harvest all records; priority 3; blocked.
- **Notes:** Do not confuse with mus.am (an ICOM Armenia directory of museums and cultural places) or museumsarmenia.am (the unified e-ticketing system, 2024). armeniantreasury.am does not resolve. Coverage is state museums, archives, and manuscript and printed holdings; private collections only with owner consent. Needs a human check or contact with the Ministry of ESCS.

### Mother See of Holy Etchmiadzin – Vache and Tamar Manoukian Matenadaran (Library)

*Մայր Աթոռ Սուրբ Էջմիածնի «Վաչե և Թամար Մանուկյան» մատենադարան* · <https://etchmiadzinlibrary.am> · AM · religious · `am.etchmiadzin`

Vache and Tamar Manoukian Matenadaran of the Mother See: about 70,000 units of Armenological and theological literature in 50 languages, including 534+ early printed books, catalogued in Koha. The *Etchmiadzin* journal (since 1944; predecessor *Ararat*, 1868–1919) is digitised on NLA Armenian Press, flib.sci.am and ARAR. Museum and archive holdings have no online catalogue.

- **Access:** web pages (no authentication); endpoint <http://koha.etchmiadzinlibrary.am/cgi-bin/koha/opac-search.pl>; metadata: marc, html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. No digital reuse terms; the footer says 'all rights reserved'. The 'Library law and rules' page lists the Law on Libraries, the library's user rules and Government decisions on library collections (including a 2013 procedure for the Armenian-script digital library); none of these grant reuse rights. Armenian Law on Copyright and Related Rights (2006) applies by default. [Terms](https://etchmiadzinlibrary.am/hy/laws-and-rules)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** The main site is a custom Yii-based CMS (built by fractal.am); robots.txt blocks only backend directories. The catalogue is a separate Koha OPAC at koha.etchmiadzinlibrary.am; its OAI-PMH reports 'OAI-PMH service is disabled'. The library links to the ArmUniCat union catalogue (armunicat.nla.am). Other site databases: encyclicals, Bible, Armenian Church directory.

### National Gallery of Armenia

*Հայաստանի ազգային պատկերասրահ* · <https://www.gallery.am> · AM · museum · `am.national-gallery`

Largest art museum in Armenia (25,000–40,000+ works of Armenian, Russian and Western European art) with regional branches. The online collection could not be inspected because of a bot challenge.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access restricted. Terms could not be read: gallery.am serves a Radware 'Verifying your browser' challenge to scripts and WebFetch, although robots.txt says 'Allow: /'. With no published licence, Armenian Law on Copyright and Related Rights (2006) applies by default; artworks by 20th-century Armenian artists are largely in copyright.
- **Integration:** harvest all records; priority 3; blocked.
- **Notes:** Branches have their own pages (e.g. Gavar, Martuni). Holdings mix Armenian, Russian and Western European art. Needs a manual browser check for the online collection and image terms.

### Yeghishe Charents Museum of Literature and Arts (GAT Museum)

*Եղիշե Չարենցի անվան գրականության և արվեստի թանգարան* · <https://gatmuseum.am> · AM · museum · `am.charents-museum`

Yeghishe Charents Museum of Literature and Arts (GAT): personal archives of Armenian writers and artists, with 362,536 objects in the manuscript department of the literary section. Its 'databases' menu lists processed fonds, published books and photographs; there is no item-level catalogue.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use unknown; attribution unknown; automated access unknown. No terms of use are published; the only notice is a footer '© 2026 GAT Museum'. Armenian Law on Copyright and Related Rights (2006) applies by default. Open Jerusalem descriptions of GAT fonds state that access needs the museum's authorization. [Terms](https://gatmuseum.am/en/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Joomla site (RSS/Atom feeds via ?format=feed). The 'ՇՏԵՄԱՐԱՆ' (databases) menu has three databases: processed fonds (articles announcing processed personal archives), published books, and photographs. Some fonds are described in the Open Jerusalem archives (AM-GAT/...), e.g. Tekeyan, Chopanyan, Oshakan.

### Komitas Museum-Institute

*Կոմիտասի թանգարան-ինստիտուտ* · <https://komitasmuseum.am> · AM · museum · `am.komitas`

Komitas Museum-Institute: Komitas's archive, letters, photographs, music library and historical recordings (about 15 tracks streamed online).

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content mixed, per item; commercial use unknown; attribution unknown; automated access allowed. No terms of use are published; the footer says only '©2026 Komitas Museum-Institute'. Armenian Law on Copyright and Related Rights (2006) applies by default. Komitas (d. 1935) is out of copyright as an author, but the museum's scans and texts carry no licence. [Terms](https://komitasmuseum.am/en)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** robots.txt allows / but disallows /api/ (the site is a JS front end with an internal API). Sections: biography, photos, recordings, Komitas's articles, letters, archival collection, music library, publications.

### Sergei Parajanov Museum

*Սերգեյ Փարաջանովի թանգարան* · <https://parajanovmuseum.am> · AM · museum · `am.parajanov`

House-museum of Sergei Parajanov with 1,766 exhibits; the online gallery shows a selection by period.

- **Holdings:** Main collection of 1,766 exhibits (About Museum page, 2026-11-02). The online Gallery shows a selection grouped by period.
- **Access:** web pages (no authentication); endpoint <https://parajanovmuseum.am/sitemap.xml>; metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. Site texts and images are the museum's property and are protected under Armenian copyright law. Use is limited to personal, informational and educational purposes. Electronic reproduction and commercial or other distribution are prohibited without permission. [Terms](https://parajanovmuseum.am/terms-and-conditions/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** robots.txt has an empty Disallow, and a sitemap is available. Parajanov's works (he died in 1990) are in copyright until 2060 under the life+70 term. Built by Concept Studio; sponsored by JTI Armenia.

### Erebuni Historical and Archaeological Museum-Reserve

<https://erebuni-museum.mus.am> · AM · museum · `am.erebuni`

Museum-reserve of the Urartian fortress Erebuni with finds from Arin Berd, Karmir Blur and Shengavit. No digital collection; the only web presence is a directory page on mus.am.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No terms or collection data are published; the only web presence is a directory page on mus.am. Armenian Law on Copyright and Related Rights (2006) applies by default.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** mus.am is a directory of cultural places (ICOM Armenia link), not a collection database. Some Erebuni objects (Urartian inscriptions) may appear in CDLI or Wikidata. Low priority: no digital collection.

### Institute of Archaeology and Ethnography, National Academy of Sciences of the Republic of Armenia

*ՀՀ ԳԱԱ Հնագիտության և ազգագրության ինստիտուտ* · <https://iae.am> · AM · research institute · `am.iae`

Institute of Archaeology and Ethnography of NAS RA. Its 580 publications are in ARAR (set IAE); excavation and folklore archives are not online.

- **Holdings:** 580 records in ARAR OAI set dLibraDigitalLibrary:IAE (institute publications), 2026-11-02. The institute library holds 44,500+ units (catalogued in Koha; no public OPAC link found).
- **Access:** OAI-PMH, web pages (no authentication); endpoint <https://arar.sci.am/oai-pmh-repository.xml?verb=ListRecords&metadataPrefix=oai_dc&set=dLibraDigitalLibrary:IAE>; metadata: dc, html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access allowed. No terms are published; the 'Terms & conditions' and 'Privacy policy' footer links are empty placeholders ('#'). Armenian Law on Copyright and Related Rights (2006) applies by default.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** The site footer shows a leftover template notice '© Սարյան ընտանիք' (Saryan family), not a real rights claim. robots.txt has an empty Disallow. The site includes a '100 archaeological monuments of Armenia' section. Excavation archives and the folklore archive are not online.

### Research on Armenian Architecture (RAA) Foundation

*Հայկական ճարտարապետությունն ուսումնասիրող հիմնադրամ (ՀՃՈՒ)* · <https://raa-am.org> · AM · foundation · `am.raa`

Research on Armenian Architecture foundation: about 699,000 digitised images of 6,132 monuments in Armenia, Western Armenia, Artsakh and Nakhichevan. The photo database is internal; the website shows galleries, 3D models and publications.

- **Holdings:** 699,250 digitized images in the RAA database by end of 2024 (RAA USA site); 6,132 documented monuments. The RAA Armenia homepage shows an older 625,000. The database is internal, not online.
- **Access:** web pages (restricted / by agreement); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. The footer states '© 2021 ՀՃՈՒ. All rights reserved'; no reuse licence is offered. The photo archive is not public and needs a direct request to RAA. [Terms](https://raa-am.org/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** raa.am does not respond; the official site is raa-am.org (WordPress, robots.txt Crawl-Delay: 20). It offers a gallery, 3D models, publications and restoration news. The RAA's 2025 report mentions a redesign of its internal photo database. Strong coverage of Western Armenia, Artsakh and Nakhichevan monuments; high-value partner, but needs an agreement.

### Public Radio of Armenia – Armenian Radio Archive

*Հայաստանի հանրային ռադիո – Հանրային ռադիոյի արխիվ* · <https://armradioarchive.am> · AM · media · `am.public-radio`

Armenian Radio Archive streaming platform for the Public Radio 'Golden Fund': 11,371 recordings online out of about 100,000 preserved, browsable by genre, decade and performer.

- **Holdings:** 11,371 item URLs in sitemap/items-1.xml (10,000) and items-2.xml (1,371), lastmod Oct 2026, read 2026-11-02. The About page says the archive preserves ~100,000 recordings; not all are online.
- **Access:** web pages (no authentication); endpoint <https://armradioarchive.am/sitemap.xml>; metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. The footer states '© 2026 Armenian Radio Archive. All rights reserved'; no licence or reuse terms are published. Recordings are streamed for listening only. Performers' and producers' rights apply under Armenian law. [Terms](https://armradioarchive.am/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Streaming platform for the 'Golden Fund' (digitized with the culture ministry since 2009). Browse by genre, decade, artist and chronology; there is a mobile app. robots.txt is 'Allow: /' with sitemaps in hy/en/ru (items, makers). Built by Digital Pomegranate, funded in honour of Hambardzum and Mary Ingilizian. The main broadcaster site is armradio.am.

### National Cinema Center of Armenia

*Հայաստանի ազգային կինոկենտրոն* · <https://ncca.am> · AM · authority · `am.cinema-center`

State film agency created in 2006 from the Hayfilm studio. Most film elements are held by the National Film Library of the National Archives; no public catalogue was found.

- **Access:** no online access (restricted / by agreement); metadata: other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. No terms could be read: ncca.am resolves but timed out on 2026-11-02. Hayfilm/Armenfilm productions are copyrighted works; Armenian Law on Copyright and Related Rights (2006) applies by default.
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** SNCO under the culture ministry, created in 2006 from the Hayfilm studio. Most film elements are held by the National Archives' National Film Library (Cine-Photo Documentation branch); access there needs special permission. Restoration work with Prasad Corp aims at screening and online access, but no public catalogue was found.

### Digital Library of Armenian Literature (DIGILIB)

<https://www.digilib.am> · AM · digital library · `am.digilib`

Full-text Digital Library of Armenian Literature run by the American University of Armenia since 1999: about 2,000 works by 625 authors, from classical to Western Armenian and diaspora writers.

- **Holdings:** Site 'About' page: 2,000 works by 625 authors (read 2026-11-02).
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use unknown; attribution unknown; automated access allowed. No terms of use or copyright statement is published. Armenian Law on Copyright and Related Rights (2006) applies by default. Classical texts (5th–18th c.) are public domain, but 20th-century Western Armenian authors may still be in copyright, and the digital editions carry no licence.
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Same site at digilib.aua.am. The bare domain digilib.am timed out; use www.digilib.am. robots.txt disallows only /111/ and /222/. Browse by theme or author; there is a login for 'My Projects'. No API.

### American University of Armenia Library – Digital Collections

*Հայաստանի ամերիկյան համալսարան* · <https://library.aua.am> · AM · library · `am.aua`

Umbrella entry for AUA library resources: the open-access repository dspace.aua.am, the Artsakh Heritage inventory (5,000+ monuments) and Armenia Hidden Gems. **Correction:** the 'Ancient / Medieval / Contemporary Armenian Literary Texts' collections listed in v1 do not exist; AUA's literary-text resource is DIGILIB.

- **Access:** OAI-PMH, web pages (no authentication); endpoint <https://dspace.aua.am/oai/request>; metadata: dc, html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use unknown; attribution unknown; automated access allowed. No library-wide reuse terms found. Repository items follow their own author licences. Armenian Law on Copyright and Related Rights (2006) applies by default.
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** library.aua.am is WordPress with Yoast and an empty Disallow in robots.txt. The catalogue is WorldCat Discovery (aualibrary.on.worldcat.org). AUA LibGuides link the Public Radio archive (armradioarchive.am). Treat DIGILIB as the primary AUA heritage source; this entry is an umbrella.

### Eastern Armenian National Corpus (EANC)

*Արևելահայերենի ազգային կորպուս* · <http://www.eanc.net> · AM · digital library · `am.eanc`

Eastern Armenian National Corpus: about 9,960 documents and 110 million tokens with morphological annotation. A linguistic resource rather than heritage records; the site timed out on 2026-11-02.

- **Holdings:** 9,960 documents, ~110 million tokens (written ~106M, oral ~3.5M), per Khurshudyan et al., DigitAm 2022 (ACL Anthology).
- **Access:** web pages (no authentication); metadata: html, other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. The corpus is described as open access for search at www.eanc.net. No licence or bulk download was found; full texts (modern fiction and press) are copyrighted and served only as search hits. [Terms](https://aclanthology.org/2022.digitam-1.5.pdf)
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** eanc.net resolves (83.149.210.101) but timed out on 2026-11-02. The project began in 2006 and went online in 2007. Developers include V. Khurshudyan (INALCO), T. Arkhangelskiy (Hamburg), M. Daniel and A. Polyakov (HSE), and V. Plungian (RAS). It has morphological and semantic annotation plus English glosses. It is a linguistic resource, not heritage records, and low priority for aggregation.

## 2. Armenian manuscripts abroad and IIIF collections

Libraries, monasteries and museums holding Armenian manuscripts outside Armenia, and the indexes that connect their digitised copies. IIIF manifests make many of them reachable without scraping.

### Index of Digitized Armenian Manuscripts (IArM)

<https://www.armenian-manuscripts-index.com/> · FR · aggregator · `int.iarm`

Index of digitised Armenian manuscripts compiled by Calfa and partners: 2,579 manuscripts in 48 digital libraries (v3.0, July 2025), with metadata (location, shelfmark, support, date, pages, size, title, genre) and IIIF manifests for 528 rows for viewing in Mirador. The website adds automatic illumination detection (Calfa Vision) and annotation. 1,780 rows point to HMML and require a login. Genres: Bible, exegesis, hagiography, history, law, linguistics, liturgy, magic, philosophy, poetry, sciences, theology.

- **Holdings:** 2,579 rows in index.tsv of Zenodo record 10.5281/zenodo.16355337 (v3.0, 22 Jul 2025); matches homepage counter; downloaded and counted 2026-11-02.
- **Access:** bulk download, web pages, IIIF (no authentication); endpoint <https://zenodo.org/records/16355337/files/index.tsv>; metadata: csv, iiif.
- **Terms of use:** metadata `CC-BY-4.0`; content mixed, per item; commercial use yes; attribution required; automated access allowed. The compiled index dataset is published on Zenodo under CC BY 4.0, so reuse incl. commercial is allowed with citation. The website footer says all rights reserved and the GitHub repo has no licence file; use the Zenodo release as the licensed copy. Images stay under each holding library's own terms. [Terms](https://zenodo.org/records/16355337)
- **Integration:** harvest all records; priority 1; integrated.
- **Notes:** Integrated 2026-11-02 with scripts/harvest_iarm.py and the portal connector `iarm_parquet`: 2,579 records from the Zenodo v3.0 release; images stay with holding libraries. Live TSV also at https://raw.githubusercontent.com/CVidalG/Index-of-Armenian-Manuscripts/refs/heads/master/index.tsv (site loads it via PapaParse). Columns: ID (Coulie sigla), Cat. Number, Location, Country, Town, Permalink, Digital Library, Support, Date, Pages, Size, Title, Note, Genre, IIIF Manifest. Top holders: HMML 1,780 (Bzommar 675, Istanbul Patriarchate ~778, Aleppo 144, Antelias 61), Gallica 182, Vatican 146, Bodleian 73, UCLA 63, Berlin 51. Use as master crosswalk for manuscript sources below. robots.txt allows all. Calfa also runs catalog.mechitar.org (Venice).

### Mekhitarist Congregation, San Lazzaro degli Armeni (Venice) - Library and Manuscript Catalogue

*Մխիթարեան Միաբանութիւն, Սուրբ Ղազար* · <https://catalog.mechitar.org/> · IT · religious · `it.mekhitarists-venice`

San Lazzaro degli Armeni holds one of the largest Armenian manuscript collections outside Armenia. The printed 8-volume catalogue (1914–1998) has been converted by Calfa into an online catalogue of 1,497 records; no manuscript images are online.

- **Holdings:** catalog.mechitar.org shows '1497 notices found' (2026-11-02). The printed 8-volume catalogue (1914-1998) has >2,500 records; Calfa says about a third of San Lazzaro mss are not yet in it. No digitised images online.
- **Access:** web pages, bulk download (no authentication); endpoint <https://raw.githubusercontent.com/calfa-co/catalog-manuscripts-venice/master/catalog.json>; metadata: json, html.
- **Terms of use:** metadata `CC-BY-NC-4.0`; content unknown; commercial use no; attribution required; automated access allowed. Raw catalogue data (OCR of the printed catalogue, by Calfa with the Mekhitarist Fathers) is CC BY-NC 4.0 per the repo README. Non-commercial reuse with attribution. No manuscript images are published, so no image terms apply. [Terms](https://github.com/calfa-co/catalog-manuscripts-venice)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Catalogue PDFs are hosted by FSL NAS RA (serials.flib.sci.am/matenagitutyun). Congregation site mechitar.org now shows only a mobile-app landing page. catalog.mechitar.org robots.txt allows all. Calfa also OCR'd >6,000 pages of letters (1750-1900), not public as data. A 2013 Armenian government grant for digitising Venice mss has no visible online output.

### Mekhitarist Congregation Vienna (Mechitharisten) - Library and Periodicals Portal

*Մխիթարեան Միաբանութիւն, Վիեննա / Wiener Mechitharisten-Congregation* · <https://mechitaristlibrary.org/> · AT · religious · `at.mekhitarists-vienna`

Mekhitarist Congregation Vienna: its periodicals portal (105,568 records, mostly issues), 730 books and 86 Armenian and Armeno-Turkish items are hosted on ARAR; the congregation also launched its own portal mechitaristlibrary.org.

- **Holdings:** OAI-PMH completeListSize on arar.sci.am (2026-11-02): set Mekhitaristcongregation (Periodicals Portal) 105,568; Mekhitaristcongregationbooks 730; armenian_and_armenogram_turkish_publications (manuscripts) 86. Records are mostly per periodical issue.
- **Access:** OAI-PMH, web pages (no authentication); endpoint <https://arar.sci.am/dlibra/oai-pmh-repository.xml?verb=ListRecords&metadataPrefix=oai_dc&set=dLibraDigitalLibrary:Mekhitaristcongregation>; metadata: dc.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access API only. mechitaristlibrary.org has a Copyright page, but it is a JavaScript app and its text could not be read; the footer shows only a copyright notice for the library. Sample oai_dc records carry no dc:rights. 2022 announcements say the material is freely accessible; no licence was found. [Terms](https://mechitaristlibrary.org/copyright)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** arar.sci.am robots.txt disallows /dlibra/results, search, download and zip paths but not OAI-PMH, so harvest via OAI. Congregation site: https://www.mechitharisten.org/. mekhitar.univie.ac.at (Armeno-Turkish project) was down for maintenance on 2026-11-02. Overlaps the Armenian national/academy digital library sources.

### Armenian Patriarchate of Jerusalem (St. James Monastery; manuscript library and Calouste Gulbenkian Library)

*Երուսաղէմի Հայոց Պատրիարքութիւն* · <https://en.wikipedia.org/wiki/Armenian_Patriarchate_of_Jerusalem> · IL · religious · `il.armenian-patriarchate-jerusalem`

St. James Monastery library with about 4,000 manuscripts (Bogharian's 11-volume catalogue, 1966–1991) and the Calouste Gulbenkian Library. Online images exist only through third parties: about 31 manuscripts from the Library of Congress microfilm survey and 2 via the Hebrew University.

- **Holdings:** About 4,000 mss per Library of Congress collection notes (1949-50 microfilm survey). Online images: about 31 St. James mss via LoC microfilm scans (IArM rows) and 2 via Hebrew University. Printed Grand Catalogue: Bogharian, 11 vols (1966-1991).
- **Access:** no online access (restricted / by agreement); metadata: other.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No institutional online catalogue or terms found. The only online images are third-party: LoC microfilm scans, which LoC states are public domain, and Hebrew University pages.
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** No official website could be confirmed: armenian-patriarchate.com is a parked domain and armenian-patriarchate.org carries spam; the URL points to a reference article. Use the LoC collection 'Manuscripts in the Libraries of the Greek and Armenian Patriarchates in Jerusalem' (IIIF manifests such as https://www.loc.gov/item/00271073938-jo/manifest.json). EAP823/EAP1142 cover St Saviour (Franciscan Custodia), not the Armenian Patriarchate.

### Catholicosate of the Great House of Cilicia, Antelias (Cilicia Library and Manuscript Center; Cilicia Museum)

*Մեծի Տանն Կիլիկիոյ Կաթողիկոսութիւն* · <https://www.armenianorthodoxchurch.org/> · LB · religious · `lb.catholicosate-cilicia`

Catholicosate of the Great House of Cilicia in Antelias: library, manuscript centre and museum. 239 manuscripts are digitised and catalogued in the HMML Reading Room (October 2025).

- **Holdings:** HMML news (Oct 2025): 239 manuscripts of the Catholicosate (digitised 2004-2005, project code ACC) are digitised, catalogued and in HMML Reading Room. IArM v3.0 (Jul 2025) listed only 61.
- **Access:** web pages (registration required); endpoint <https://www.vhmml.org/readingRoom/>; metadata: html, json.
- **Terms of use:** metadata `CC-BY-4.0`; content restricted; commercial use no; attribution required; automated access restricted. Online access is only via HMML Reading Room: catalogue metadata is CC BY 4.0, but images need a free vHMML login. Users may not copy or redistribute partner images without HMML authorisation. The Catholicosate keeps image rights. [Terms](https://www.vhmml.org/terms)
- **Integration:** link / enrich only; priority 3; candidate.
- **Notes:** Official site returned HTTP 403 to scripted requests (bot protection); content not checked. The Cilicia Library is revising its Antelias and Aleppo catalogues (Armenian Prelacy news, Aug 2025). The Aleppo diocese mss (IArM: 144 via HMML) are a separate HMML repository. No separate online museum database found.

### Holy Savior (Vank) Cathedral museum and Nerses Shnorhali Library, New Julfa, Isfahan

*Ամենափրկիչ վանք, Նոր Ջուղա / کلیسای وانک* · <https://www.vank.ir/> · IR · religious · `ir.new-julfa`

Holy Savior (Vank) Cathedral museum and Nerses Shnorhali Library in Isfahan, with more than 700 manuscripts; no online catalogue.

- **Holdings:** 'More than 700 manuscripts' in the library per secondary sources (Wikipedia and others, 2026-11-02 search); not verified from an institutional source. No online catalogue.
- **Access:** no online access (restricted / by agreement); metadata: other.
- **Terms of use:** metadata `unknown`; content all rights reserved; commercial use unknown; attribution unknown; automated access unknown. vank.ir (Armenian Prelacy of Isfahan and Southern Iran) footer reserves all rights for the Prelacy. No digitised manuscripts or reuse terms found. [Terms](https://www.vank.ir/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** vank.ir (fa, hy, en) has pages for the Nerses Shnorhali Library, a virtual tour and a music archive; Joomla site. Print catalogues of New Julfa mss exist (e.g. a catalogue series with Peria/Charmahal and private collections). Bodleian MS. Arm. d. 13 and Getty Ms. Ludwig II 7 are New Julfa-made mss held elsewhere.

### Korneli Kekelidze Georgian National Centre of Manuscripts (Tbilisi)

*კორნელი კეკელიძის სახელობის საქართველოს ხელნაწერთა ეროვნული ცენტრი* · <https://manuscript.ge/> · GE · archive · `ge.manuscripts-centre`

Korneli Kekelidze National Centre of Manuscripts in Tbilisi: 311 Armenian manuscripts, including an 8th–9th-century Georgian-Armenian palimpsest and Gospels of 1307. No online images.

- **Holdings:** Oriental Manuscripts Fund page (manuscript.ge/aghmosavlur-xelnawerta-fondi, 2026-11-02): Armenian collection (ARM) has 311 manuscripts in Grabar and Ashkharabar. Earliest: Georgian-Armenian palimpsest A-491 (8th-9th c., Agathangelos); earliest dated Gospels Arm-18 (1307); Cilician hymnal Arm-173 (1329).
- **Access:** web pages (restricted / by agreement); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use unknown; attribution unknown; automated access allowed. Site footer: 'All Rights Reserved © 2025 Manuscript'. No open licence or online Armenian manuscript images found. Reading-room access on site. [Terms](https://manuscript.ge/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** New site in 'test mode' (Georgian, EN toggle). robots.txt allows all, but there is no catalogue or API for Armenian mss. EAP848 (Grishashvili Library-Museum, Tbilisi) is a separate EAP project. Armenian items also in other fonds (e.g. palimpsests).

### Biblioteca Apostolica Vaticana - DigiVatLib (Vat. arm., Borg. arm. and other fonds)

*Biblioteca Apostolica Vaticana* · <https://digi.vatlib.it/> · VA · library · `va.bav`

Vatican Apostolic Library: about 146 Armenian manuscripts (Borg. arm., Vat. arm. and others) digitised in DigiVatLib with IIIF manifests.

- **Holdings:** IArM v3.0: 146 BAV Armenian mss (Borg. 90, Vat. 48, Barb. 4, Chig. 2, Arch. 2), 137 with IIIF manifests. Fondo pages digi.vatlib.it/mss/Vat.arm and /mss/Borg.arm list 42 and 83 distinct shelfmarks (2026-11-02).
- **Access:** IIIF, web pages (no authentication); endpoint <https://digi.vatlib.it/iiif/MSS_Vat.arm.1/manifest.json>; metadata: iiif, html.
- **Terms of use:** metadata `unknown`; content all rights reserved; commercial use conditional; attribution required; automated access restricted. The DigiVatLib footer says text and images may not be reproduced in any form without BAV authorisation. Manifests carry 'Images Copyright Biblioteca Apostolica Vaticana' and no licence. Publication or professional use needs a permission request and fees, with shelfmark credit 'by permission of BAV, all rights reserved'. Linking and viewing via IIIF is practical, but republishing images is not. [Terms](https://www.vatlib.it/en/information-readers/fotoriproduzione-uso-professionale.html)
- **Integration:** link / enrich only; priority 3; candidate.
- **Notes:** IIIF v2 manifest pattern: https://digi.vatlib.it/iiif/MSS_{Fondo}.{n}/manifest.json (e.g. MSS_Borg.arm.1). robots.txt disallows /search, /*/search, /*/detail/*, /about, /news and sets Crawl-delay 10 (Bingbot 30); /iiif and /mss/ are not disallowed. Metadata reuse terms not stated.

### British Library - Armenian manuscripts (Archives and Manuscripts Catalogue / Digitised Manuscripts)

<https://www.bl.uk/collection/digitised-manuscripts-archives> · GB · library · `gb.bl`

British Library Armenian manuscripts (about 82 non-EAP catalogue records). Since the October 2023 cyberattack its own digitised Armenian manuscripts are not available online.

- **Holdings:** Interim catalogue searcharchives.bl.uk, facet Language=Armenian, 2026-11-02: 5,198 records, of which 5,116 are EAP. Non-EAP: Oriental Manuscripts 52, Western Manuscripts 14, India Office 13, Music 3 (=82 records, not all are codices). Digitised platform facet: 32 'BL legacy Universal Viewer (unavailable)', 1 'BL legacy Digitised Manuscripts (unavailable)', 0 on the new 2024- platform.
- **Access:** web pages, API, IIIF (no authentication); endpoint <https://searcharchives.bl.uk/catalog/{record_id}.json>; metadata: json, html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution required; automated access allowed. New IIIF v3 manifests link rights to the BL page on reusing images of unpublished manuscripts. Secondary sources say many digitised manuscript images carry the Public Domain Mark, with a request to credit the BL; other items vary. No explicit catalogue metadata licence was found. The terms page could not be fetched here (blocked to tools). [Terms](https://www.bl.uk/help/how-to-reuse-images-of-unpublished-manuscripts)
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** Interim Blacklight catalogue has JSON per record (append .json) and facets (language_ssim, collection_area_ssi, digitised content platform). robots.txt on bl.uk and searcharchives allows all. New manifests: https://bl.digirati.io/iiif/ark:/81055/... viewed via iiif.bl.uk/uv. Interim catalogue holds only pre-Oct-2023 records. BL also hosts EAP Armenian material (see gb.bl-eap).

### British Library Endangered Archives Programme (EAP) - Armenian projects

<https://eap.bl.uk/> · GB · digital library · `gb.bl-eap`

Endangered Archives Programme projects with Armenian material: **EAP180** (rare Armenian books and periodicals of the Fundamental Scientific Library NAS RA, 4,227 records) and **EAP613** (National Library of Armenia maps, periodicals and newspapers, 477 records), plus EAP675 and EAP1145 (Armenians in Bulgaria) and EAP001 (Iranian photography). **Correction:** v1 described EAP613 as the rare-books project.

- **Holdings:** BL interim catalogue, Language=Armenian AND Collection Area=Endangered Archives Programme: 5,116 records (2026-11-02); 4,227 in 'Preservation through digitisation of the endangered Armenian rare books...(phase 1)' (EAP180) and 477 in 'Armenian maps, periodicals and newspapers' (EAP613). EAP613/2 alone = 41,715 TIFF images.
- **Access:** web pages, IIIF, API (no authentication); endpoint <https://searcharchives.bl.uk/?f%5Bcollection_area_ssi%5D%5B%5D=Endangered+Archives+Programme&f%5Blanguage_ssim%5D%5B%5D=Armenian>; metadata: json, html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use conditional; attribution required; automated access restricted. EAP material is shared for research and non-commercial use. Where copyright applies, applicants grant a CC BY-NC licence, so the default is CC BY-NC but item terms vary. Commercial requests go back to the archive owner. Catalogue records note 'access is for research purposes only'; JPEG download depends on the custodian. The policy page was read via search snippets because eap.bl.uk blocks scripts. [Terms](https://eap.bl.uk/reuse-collections-and-takedown-policy)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** eap.bl.uk sits behind an AWS WAF JavaScript challenge (HTTP 202, empty body) for scripted clients; harvest metadata from searcharchives.bl.uk instead (JSON per record, e.g. /catalog/032-003382201.json = EAP613/2). Catalogue 'Digitised Content' links point to eap.bl.uk/collection/EAP613-2 etc. Overlap: EAP180/EAP613 content also exists at NLA/FSL Armenian digital libraries.

### Bodleian Libraries, University of Oxford (Digital Bodleian) - Armenian Manuscripts and Printed Books

<https://digital.bodleian.ox.ac.uk/collections/armenian/> · GB · library · `gb.bodleian`

140 Armenian manuscripts (oldest from the 11th century), images from 79 online; about 14 were fully photographed in the Carnegie project (2021/22), many others are palaeographic samples. A TEI catalogue is on GitHub.

- **Holdings:** Collection page (checked 2026-11-02): 140 Armenian mss held, images from 79 mss online. IIIF collection 'armenian' lists 94 manifests (70 unique shelfmarks). Online TEI catalogue repo has 127 entries in collections/. IArM lists 73.
- **Access:** IIIF, web pages, bulk download (no authentication); endpoint <https://iiif.bodleian.ox.ac.uk/iiif/collection/armenian>; metadata: iiif, json, other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use conditional; attribution required; automated access allowed. Most images are CC BY-NC 4.0 (stated in each IIIF manifest's attribution). Non-commercial reuse needs shelfmark, institution, link and licence credit. Commercial use needs permission and fees. No metadata licence is stated on Digital Bodleian, and the TEI catalogue repo has no licence file. [Terms](https://digital.bodleian.ox.ac.uk/terms/)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** TEI P5 catalogue on GitHub: https://github.com/bodleian/armenian-mss (no licence); web catalogue https://armenian.bodleian.ox.ac.uk/ is behind Anubis proof-of-work anti-bot (not scriptable). Digital Bodleian robots.txt only blocks register/derivatives paths. Armenian palaeography site: armenianpalaeography.bodleian.ox.ac.uk. Overlaps IArM (73) and Biblissima IIIF Collections.

### Chester Beatty (Dublin) - Armenian manuscripts

<https://chesterbeatty.ie/> · IE · museum · `ie.chester-beatty`

Chester Beatty library in Dublin: Armenian manuscripts with IIIF manifests and CC BY 4.0 images.

- **Holdings:** IArM v3.0: 6 digitised Armenian items (Arm 551, 576.1, 576.2, 578, 614, 624). Full digitised count unknown: viewer search is robots-disallowed and behind Anubis.
- **Access:** IIIF, web pages (no authentication); endpoint <https://viewer.cbl.ie/viewer/api/v1/records/Arm_578/manifest/>; metadata: iiif, html.
- **Terms of use:** metadata `unknown`; content open licences; commercial use yes; attribution required; automated access restricted. Digital images of collection objects are CC BY 4.0 unless stated otherwise: reuse, remix and commercial use allowed with formal attribution to the Chester Beatty. Objects under other copyright need contact with photographic services. No explicit metadata licence. [Terms](https://chesterbeatty.ie/about/copyright-2/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Goobi viewer at viewer.cbl.ie (Anubis proof-of-work on HTML pages). IIIF manifests at /viewer/api/v1/records/{PI}/manifest/ answered directly (license field is the placeholder 'iiif_license'). robots.txt disallows /viewer/search/, /viewer/oai, PDFs; Crawl-delay 10. Museum closed to visitors 15 Jun-Dec 2026.

### Bayerische Staatsbibliothek - Digitale Sammlungen / MDZ (Cod.armen.)

*Bayerische Staatsbibliothek, Münchener DigitalisierungsZentrum* · <https://www.digitale-sammlungen.de/> · DE · library · `de.bsb`

Bavarian State Library: 30 Armenian manuscripts (Cod.armen.), several digitised with IIIF and Public Domain Mark, plus printed books and recordings.

- **Holdings:** bavarikon: BSB holds 30 Armenian manuscripts (Cod.armen.); undated page. IArM v3.0 lists 5 digitised (e.g. Cod.armen. 1 = bsb00070502, Cod.armen. 6). Web search UI is JS-only, so no exact digitised count.
- **Access:** IIIF, web pages, API (no authentication); endpoint <https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00070502/manifest>; metadata: iiif, mets, mods.
- **Terms of use:** metadata `unknown`; content public domain; commercial use yes; attribution not required; automated access allowed. Each object carries a rights statement. Cod.armen. manifests use Public Domain Mark 1.0, which per the MDZ FAQ allows copying, modification and commercial use without permission. Other categories (in copyright, Google scans non-commercial) differ. The FAQ states no metadata licence. [Terms](https://www.digitale-sammlungen.de/en/faq)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** IIIF Presentation v2/v3 and Image v3 APIs at api.digitale-sammlungen.de; METS/MODS via api.digitale-sammlungen.de/dfg/mets/mods/v1/digitalobjects/identifier/{bsbid}. robots.txt allows all. Older daten.digitale-sammlungen.de/~db/... permalinks (used in IArM) are legacy. IArM also links BSB-hosted images of Matenadaran M6200. BSB also has Armenian printed books and audio (Europeana).

### Real Biblioteca del Monasterio de San Lorenzo de El Escorial - Real Biblioteca Digital

*Real Biblioteca del Monasterio de San Lorenzo de El Escorial (Patrimonio Nacional)* · <https://rbme.patrimonionacional.es/> · ES · library · `es.escorial`

Royal Library of El Escorial. **Correction:** the 16th-century 'sermons of Ephraem Syrus' manuscript cited in v1 (Psi-II-9) is Greek; no Armenian-language manuscripts were found in the digital library.

- **Holdings:** Omeka S API search, 2026-11-02: 'armenio' gives 3 hits, 'armen' gives 17, 'Armenian' and 'armenia' give 0. None are Armenian-language mss; hits are Greek and Latin codices. Total items 1,518.
- **Access:** API, IIIF, web pages (no authentication); endpoint <https://rbme.patrimonionacional.es/api/items?search=armenio>; metadata: json, iiif.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access allowed. No licence on items or IIIF manifests (no rights or license fields). The Patrimonio Nacional legal notice is a generic IP and website notice (bans framing) with no open licence for images or metadata. [Terms](https://www.patrimonionacional.es/aviso-legal)
- **Integration:** not a metadata source; priority 4; not applicable.
- **Notes:** No Armenian-language manuscripts found in the Real Biblioteca Digital; the 'Ephraem Syrus' manuscript cited in v1 (Psi-II-9) is Greek. Kept only to document the correction. Omeka S REST API is public: /api/items?search=..., IIIF v2 manifests at rbdigital.realbiblioteca.es/files/manifests/{shelfmark}.json.

### Musée Arménien de France (Fondation Nourhan Fringhian), Paris

*Musée arménien de France* · <https://www.musee-armenien-de-france.org/> · FR · museum · `fr.musee-armenien`

Musée Arménien de France (Fondation Nourhan Fringhian): manuscripts (11th–18th c.), religious art and archaeology. 32 manuscripts are digitised by IRHT on ARCA and aggregated by Biblissima.

- **Holdings:** 32 MAF manuscripts digitised by IRHT on ARCA with IIIF manifests: IArM v3.0 (32 rows) and Biblissima IIIF Collections facet 'Musée Arménien de France de Paris' = 32 (2026-11-02).
- **Access:** IIIF, web pages (no authentication); endpoint <https://api.irht.cnrs.fr/ark:/63955/fxruw2qi5pkg/manifest.json>; metadata: iiif.
- **Terms of use:** metadata `unknown`; content restricted; commercial use no; attribution required; automated access unknown. IRHT/ARCA IIIF manifests for MAF manuscripts declare CC BY-NC 3.0 with attribution to the Musée Arménien de France. Non-commercial reuse with credit; commercial use needs permission. Museum's own terms not found (site unreachable). [Terms](http://creativecommons.org/licenses/by-nc/3.0/deed.fr)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Museum website timed out on 2026-11-02 (both www and bare domain). ARCA permalinks: https://arca.irht.cnrs.fr/ark:/63955/md03cz30sp89 (MAF126). Use IArM rows 'Musée Arménien de France - IRHT' as the item list.

### Biblissima+ (portal, IIIF Collections of Manuscripts and Rare Books, data.biblissima.fr)

*Biblissima+* · <https://portail.biblissima.fr/> · FR · aggregator · `fr.biblissima`

French manuscript and rare-book infrastructure aggregating IIIF manifests (217 Armenian results, mostly BnF and MAF) and authority data.

- **Holdings:** IIIF Collections search 2026-11-02: 'arménien' = 217 results (BnF/Gallica 183, MAF/ARCA 32, BSB 1, Blois 1; language facet Armenian 173). 'armenian' = 11 more (Bodleian, e-codices). Some overlap possible.
- **Access:** IIIF, web pages, SPARQL, API (no authentication); endpoint <https://iiif.biblissima.fr/collections/search?q=arm%C3%A9nien>; metadata: iiif, rdf, html.
- **Terms of use:** metadata `etalab-2.0`; content mixed, per item; commercial use conditional; attribution required; automated access restricted. Biblissima authority data (data.biblissima.fr Wikibase) is under the French Licence Ouverte / Etalab 2.0, which allows commercial reuse with source attribution (not an SPDX id here, so marked custom). Aggregated records and images keep each holding library's terms (e.g. Gallica, ARCA CC BY-NC, Bodleian CC BY-NC). [Terms](https://data.biblissima.fr/w/Accueil/en)
- **Integration:** link / enrich only; priority 3; candidate.
- **Notes:** portail.biblissima.fr, data.biblissima.fr and its SPARQL endpoint are behind Anubis proof-of-work anti-bot (scripted access blocked 2026-11-02). iiif.biblissima.fr/collections is reachable; per-item manifest copies like iiif.biblissima.fr/collections/manifest/{hash}. Licence text read via search snippet of data.biblissima.fr home page.

### Walters Art Museum - Armenian manuscripts (Digital Walters)

<https://art.thewalters.org/> · US · museum · `us.walters`

Walters Art Museum: 11 Armenian manuscripts (W.537–W.547), images and descriptions CC0, mirrored on OPenn.

- **Holdings:** IArM v3.0: 11 Walters Armenian mss (W.537-W.547). OPenn mirror of Digital Walters (2018 snapshot) has W537, W538, W539, W543 in that range (checked 2026-11-02).
- **Access:** bulk download, web pages (no authentication); endpoint <https://openn.library.upenn.edu/Data/_0020/Data/WaltersManuscripts/>; metadata: other, html.
- **Terms of use:** metadata `CC0-1.0`; content open licences; commercial use yes; attribution not required; automated access allowed. Since 6 Feb 2013 all Walters manuscript images and descriptions are CC0 (also GFDL); the earlier non-commercial restriction was dropped. No permission is needed. Citation and a courtesy copy to the curator are requested but not required. [Terms](https://openn.library.upenn.edu/Data/_0020/03_ReadMe.html)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** thedigitalwalters.org failed TLS (HTTP 525) and art.thewalters.org / thewalters.org returned 403 to scripted requests on 2026-11-02. Use the OPenn mirror (_0020) with TEI msDesc + images per W-number. Walters is also listed among vHMML CC partners. IArM permalinks point to thedigitalwalters.org/Data/WaltersManuscripts/html/W537 etc.

### J. Paul Getty Museum - Armenian manuscripts

<https://www.getty.edu/> · US · museum · `us.getty`

J. Paul Getty Museum: Armenian manuscripts including the Zeytun Gospels canon tables by T'oros Roslin (1256) and the Mesrop of Khizan Gospels (Isfahan, 1615); collection data CC0.

- **Holdings:** IArM v3.0 lists 4 Getty objects (e.g. collection objects 1351, 1358). Holdings include Zeyt'un Gospels canon-table leaves by T'oros Roslin (Ms. 59, 1256) and the Mesrop of Khizan Gospels (Ms. Ludwig II 7, Isfahan 1615). Getty SPARQL not queryable anonymously, so no exact count.
- **Access:** API, SPARQL, IIIF, web pages (no authentication); endpoint <https://data.getty.edu/museum/collection/activity-stream>; metadata: json, rdf, iiif.
- **Terms of use:** metadata `CC0-1.0`; content open licences; commercial use yes; attribution not required; automated access allowed. Getty API docs state collection data is CC0. Open Content images of public-domain works are free to download and reuse without restriction (CC0); check each object, since some images are not Open Content. [Terms](https://data.getty.edu/museum/collection/docs/)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Linked Art JSON-LD REST at data.getty.edu/museum/collection/object/{uuid}; activity stream works without auth (4.56M activities). The SPARQL endpoint (/museum/collection/sparql) returned 401 'Authorization token is wrong or missing' to anonymous GET/POST on 2026-11-02. IIIF Image API on media.getty.edu. Docs URL returned 404 to curl and TLS error to WebFetch; licence taken from Getty docs via search snippet. Zeyt'un leaves: ownership settled with the Catholicosate of Cilicia (2015), which donated them to the Getty.

### OPenn (University of Pennsylvania Libraries), incl. Free Library of Philadelphia and Walters mirror

<https://openn.library.upenn.edu/> · US · digital library · `us.penn-openn`

University of Pennsylvania OPenn: one Armenian manuscript (LJS 443) plus the Walters mirror.

- **Holdings:** Only clear Armenian item found on OPenn: UPenn LJS 443 (calendar texts, Armenia, after 1416), repo 0001. FLP Lewis T451 (Armenian fragment) is on FLP's own site, not in OPenn 0023 contents. Plus Walters Armenian mss in OPenn mirror _0020 (see us.walters). Checked via *_contents.csv and Digital Scriptorium, 2026-11-02.
- **Access:** bulk download, web pages (no authentication); endpoint <https://openn.library.upenn.edu/Data/0001/ljs443/>; metadata: other, csv.
- **Terms of use:** metadata `CC-BY-4.0`; content public domain; commercial use yes; attribution required; automated access allowed. Licences are per repository. Penn LJS (0001) and Penn Libraries (0002): images Public Domain Mark, metadata CC BY 4.0. Free Library (0023): images PDM, metadata CC0. Walters mirror: CC0. All OPenn content is public domain or Free Cultural Works CC licences. [Terms](https://openn.library.upenn.edu/html/0001.html)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Per-repo contents CSVs at /Data/{repo}_contents.csv (title only, no language column); TEI msDesc per item. robots.txt only disallows *.tif/*.tiff for crawlers. Server very slow (20-40 s per request) on 2026-11-02. Digital Scriptorium (search.digital-scriptorium.org, Language=Armenian) lists 43 US Armenian items, useful for Penn/FLP/Chicago crosswalk.

### Hill Museum & Manuscript Library (HMML) - vHMML / HMML Reading Room

<https://www.vhmml.org/> · US · library · `us.hmml`

Hill Museum & Manuscript Library: the largest single body of digitised Armenian manuscripts (about 1,780 in IArM: Bzommar, the Armenian Patriarchate of Istanbul, Antelias, Aleppo, Iraq, Lviv), viewable after free registration.

- **Holdings:** IArM v3.0 rows with Digital Library=HMML: 1,780 (Lebanon 794 incl. Bzommar 675; Turkey 778 = Istanbul Patriarchate; Syria 146; Iraq 51). HMML says >760 Istanbul Patriarchate mss viewable and 239 Antelias mss (Oct 2025). Data Portal count not taken (Turnstile).
- **Access:** web pages, bulk download (registration required); endpoint <https://www.vhmml.org/dataPortal>; metadata: json, html.
- **Terms of use:** metadata `CC-BY-4.0`; content restricted; commercial use no; attribution required; automated access restricted. Reading Room and Museum metadata are CC BY 4.0. Viewing images needs a free account. Users agree not to copy or redistribute partner-library images without HMML authorisation; misuse can suspend the account. Only HMML-owned items are CC BY-NC 4.0. [Terms](https://www.vhmml.org/terms)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Data Portal exports JSON (curated or full Reading Room dataset) but is protected by Cloudflare Turnstile; do not automate, request the dataset from HMML (help@vhmml.org) instead. robots.txt disallows /image/, /image/manifest/folio and /user/acceptReadingRoomAgreement. Stable record URIs: https://w3id.org/vhmml/readingRoom/view/{id}. Largest single source of digitised Armenian mss (Bzommar, Istanbul, Antelias, Aleppo, Baghdad, Mosul, Lviv).

### Bibliothèque Orientale, Université Saint-Joseph (Beirut)

*Bibliothèque Orientale - Université Saint-Joseph de Beyrouth* · <https://www.usj.edu.lb/> · LB · library · `lb.usj-bibliotheque-orientale`

Bibliothèque Orientale of Université Saint-Joseph. **Correction:** the 2,929 manuscripts catalogued via HMML cover all languages; only about 7 are Armenian.

- **Holdings:** IArM v3.0: 7 Armenian mss of USJ Bibliothèque orientale in HMML Reading Room. HMML's 2,929 figure (May 2024) is the total catalogued for the whole library, all languages, mostly Arabic Christian.
- **Access:** web pages (registration required); endpoint <https://www.vhmml.org/readingRoom/>; metadata: html, json.
- **Terms of use:** metadata `CC-BY-4.0`; content restricted; commercial use no; attribution required; automated access restricted. Access is via HMML Reading Room: catalogue metadata CC BY 4.0, images need login, and redistribution of images needs HMML authorisation. No USJ-specific reuse terms found. [Terms](https://www.vhmml.org/terms)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** HMML repository page: hmml.org/collections/repositories/lebanon/université-saint-joseph--bibliothèque-orientale/ (in progress). Same HMML access blockers as us.hmml. Doc URL www.usj.edu.lb/bibliotheque/ not checked; USJ homepage reachable.

## 3. International aggregators and national digital libraries

General collections in which Armenian records must be selected with the matcher. Most publish metadata under CC0 or another open licence, which makes them the fastest route to multilingual coverage.

### Europeana

<https://www.europeana.eu> · NL · aggregator · `eu.europeana`

Europe's cultural heritage platform (60+ million items) and the model for Armeniana's infrastructure (EDM, IIIF, API). Armenian content includes manuscripts (e.g. Wellcome Collection), Armenian ornaments (Schola Graphidis, Budapest), art from the Albertina, Armenian songs (Bavarian State Library), Romanian Radio recordings and photographs of the massacres (TopFoto).

- **Holdings:** Europeana Search API (wskey=api2demo), 2026-11-02: multilingual OR query (armenia, armenian, armenien, arménien, armeno, armenio, armeens, армянский, Հայաստան) = 18,393; query 'armenian' = 7,582; 'where:Armenia' = 12,295; 'where:(Armenia OR Hayastan OR Arménie OR Armenien)' = 12,740; qf=LANGUAGE:hy = 0. Language facet of 'armenian' results: en 5,197, mul 663, de 545, fr 317, hu 238.
- **Access:** API, OAI-PMH, IIIF, SPARQL, bulk download, web pages (API key required); endpoint <https://api.europeana.eu/record/v2/search.json>; metadata: edm, json, rdf.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution not required; automated access API only. All Europeana metadata is CC0; each digital object carries its own rights statement in edm:rights (for the 7,582 'armenian' hits: CC0 4,381, CC BY 984, InC 492, CC BY-NC 320, CC BY-SA 305, NoC-NC 265, NoC-OKLR 221, PDM 172). Search/Record APIs need a free API key that is personal to one application and must not be shared (api2demo is for testing only); the API FAQ says there is no throttling but asks for a short pause between calls, and the terms let Europeana impose reasonable limits. IIIF and SPARQL work without a key. [Terms](https://www.europeana.eu/en/rights/terms-of-use)
- **Integration:** filter Armenian records with the matcher; priority 1; planned.
- **Notes:** Best recall: multilingual OR keyword query plus where:(...) place query, then dedupe by record id. LANGUAGE:hy facet is empty, so do not rely on the language facet. Bulk: per-dataset EDM XML zips at https://download.europeana.eu/dataset/XML/ (open directory, verified); OAI-PMH at https://api.europeana.eu/oai (Identify verified). Overlaps: DDB, Hispana, Gallica partner content, Institut de France (Mazarine), Polona/FBC, Wellcome; dedupe against national aggregators.

### German Digital Library

*Deutsche Digitale Bibliothek* · <https://www.deutsche-digitale-bibliothek.de> · DE · aggregator · `de.ddb`

German national aggregator: 8,461 Armenia-related objects, 2,748 of them in Armenian (language facet `arm`).

- **Holdings:** DDB Solr search endpoint /2/search/index/search/select, 2026-11-02: q='armenisch OR armenien OR armenier OR armenian' = 8,461; q='armenisch' = 4,927; fq=language_fct:arm (Armenian-language objects) = 2,748.
- **Access:** API, web pages (API key required); endpoint <https://api.deutsche-digitale-bibliothek.de/2/search/index/search/select>; metadata: json, edm.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution required; automated access API only. All metadata delivered by the DDB API is CC0; digital objects (images, media) keep the rights statement of each provider (license field per record). The terms require an API key obtained in a 'My DDB' account and ask that applications show a 'Powered by Deutsche Digitale Bibliothek' label; DDB reserves the right to limit request volume (no number published). Observed: the /2/search/index Solr endpoint answered without a key, while the classic /search endpoint returned 403 without one. [Terms](https://www.deutsche-digitale-bibliothek.de/content/terms/api)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** language_fct:arm is a reliable Armenian-language filter; combine with keyword query for subject matter. Fields include license, metadata_rights, provider, place_fct. DDB is Germany's aggregator to Europeana (overlap), and includes the Deutsches Zeitungsportal newspapers. Obtain a key before production use, since keyless access may be withdrawn.

### Gallica (Bibliothèque nationale de France)

*Gallica – Bibliothèque nationale de France* · <https://gallica.bnf.fr> · FR · digital library · `fr.gallica`

Digital library of the BnF and partners: about 489 Armenian items (226 books, 199 manuscripts, 40 sound recordings, 15 periodicals, 8 maps; Dec 2025 count). The BnF holds about 350 Armenian manuscripts and a large share of 16th–17th-century Armenian printing (v1 figures, not re-verified).

- **Holdings:** Figure 489 is the doc's Dec 2025 count (books 226, manuscripts 199, sound 40, press 15, maps 8, images 1); it could not be re-verified on 2026-11-02 because gallica.bnf.fr (including SRU) returned HTTP 403 to scripts and to WebFetch.
- **Access:** SRU, IIIF, API, web pages (no authentication); endpoint <https://gallica.bnf.fr/SRU?operation=searchRetrieve&version=1.2&query=dc.language%20all%20%22arm%22>; metadata: dc, iiif.
- **Terms of use:** metadata `etalab-2.0`; content mixed, per item; commercial use conditional; attribution required; automated access restricted. Descriptive metadata of Gallica documents is published under the French Licence Ouverte (Etalab). Non-commercial reuse of reproductions is free with the credit 'Source gallica.bnf.fr / BnF'; commercial reuse requires a licence and fee from the BnF (utilisation.commerciale@bnf.fr), partner-library items follow the partner's conditions, and in-copyright works are excluded. The IIIF and SRU APIs need no key and are open except for abusive use; no numeric rate limit is published, and plain scripts were blocked with 403 during the 2026-11-02 check. [Terms](https://gallica.bnf.fr/edit/und/conditions-dutilisation-des-contenus-de-gallica)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Query SRU with dc.language all "arm" plus gallica all "arménien"; IIIF manifests at https://gallica.bnf.fr/iiif/ark:/12148/{id}/manifest.json. data.bnf.fr (catalogue linked data, SPARQL) is also under Licence Ouverte and useful for Armenian authors. Gallica harvests partner libraries (e.g. Institut de France/Mazarine), so dedupe. Expect 403/anti-bot responses; use a low request rate and a descriptive User-Agent.

### BULAC (University Library of Languages and Civilizations)

*Bibliothèque universitaire des langues et civilisations (BULAC)* · <https://www.bulac.fr> · FR · library · `fr.bulac`

University library of languages and civilisations (INALCO) and a central portal for Armenian studies in France. Its own digital library BiNA holds 984 Armenian-domain items, including 949 items of the Paris daily *Haratch* and a collection of Armenian periodicals; the print Armenian collection exceeds 6,600 works.

- **Holdings:** BiNA digital library Omeka S API, 2026-11-02: item set 'Domaine arménien' (id 359095) = 984 items, all tagged language arm; subsets include 'Haratch' (949 items), 'Fonds de périodiques arméniens' (983), 'Midk ev Arvest' (34). fulltext_search 'arménien' = 991. Print holdings are larger (a 2023 interview cites over 6,600 works in the Armenian collection).
- **Access:** API, IIIF, web pages (no authentication); endpoint <https://bina.bulac.fr/api/items?item_set_id=359095>; metadata: json, rdf, iiif.
- **Terms of use:** metadata `etalab-2.0`; content mixed, per item; commercial use conditional; attribution required; automated access unknown. Unless stated otherwise, BiNA notices and texts are reusable under the Licence Ouverte (Etalab) with source citation, and images of public-domain documents are marked Public Domain Mark 1.0. Item-level dcterms:rights overrides this: in the Armenian set 675 items are CC BY-NC 4.0 (largely Haratch), 308 public domain, 1 rights reserved. The Omeka S REST API needs no key; no rate limit is published. [Terms](https://bina.bulac.fr/s/bina/page/informations-techniques-et-juridiques)
- **Integration:** harvest all records; priority 1; integrated.
- **Notes:** Integrated 2026-11-02 with scripts/harvest_bina.py and the portal connector `bina_parquet`: 984 records, item-level rights kept (675 CC BY-NC 4.0, 308 Public Domain Mark, 1 in copyright shown without image). Harvest via Omeka S API with item_set_id=359095 (JSON-LD, totals in the Omeka-S-Total-Results header). The IIIF Server module is installed, so manifests are available per item. Haratch overlaps with ARAM's Haratch collection and archive.org HARATCH_YYYY-MM uploads; respect CC BY-NC for those.

### Bibliothèque Mazarine

<https://www.bibliotheque-mazarine.fr> · FR · library · `fr.mazarine`

Historic Paris library with rare Armenian printed books and virtual exhibitions on Armenian printing. Its digital library moved to the shared Institut de France platform (bibnum.institutdefrance.fr), where only 3 Armenian prints are online.

- **Holdings:** Bibliothèques numériques de l'Institut de France search, 2026-11-02: 'arménien' = 3 results (all Bibliothèque Mazarine, printed books, 16th-17th c., incl. Rome editions with Granjon Armenian type); 'Armenian' = 0. Physical Armenian print holdings are not counted here.
- **Access:** OAI-PMH, IIIF, web pages (no authentication); endpoint <https://bibnum.institutdefrance.fr/oai>; metadata: dc.
- **Terms of use:** metadata `custom`; content restricted; commercial use conditional; attribution required; automated access allowed. Images and metadata of the Institut de France digital libraries are free for non-commercial reuse under CC BY-NC-ND 3.0 FR with a prescribed citation (author, title, date, holding library, shelfmark, permalink). Commercial reuse needs prior authorisation and a fee (bibnum@institutdefrance.fr). OAI-PMH and IIIF are offered for harvesting (the site says Gallica, Isidore and Europeana harvest it); no rate limit is published. [Terms](https://bibnum.institutdefrance.fr/mentions-legales)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** OAI sets per library/type, e.g. oai:bibnum.institutdefrance.fr:sets:1:24224 (Mazarine: Imprimés). The OAI repository started 2024-10-10. Same records reach Gallica and Europeana, so dedupe. Physical Armenian holdings must be found in the Sudoc/Calames catalogues.

### FranceArchives

*FranceArchives – Portail national des archives* · <https://francearchives.gouv.fr> · FR · portal · `fr.francearchives`

French national archives portal aggregating finding aids, with an RDF (RiC-O) dump and SPARQL endpoint.

- **Access:** SPARQL, bulk download, web pages (no authentication); endpoint <https://sparql.francearchives.gouv.fr/sparql>; metadata: ead, rdf.
- **Terms of use:** metadata `etalab-2.0`; content mixed, per item; commercial use conditional; attribution required; automated access restricted. Datasets built from partner data are offered under the French Licence Ouverte 2.0 (Etalab), which allows commercial reuse with source attribution. Digitised documents remain under each archive service's own reuse rules. Machine access is currently gated by a JS/cookie challenge, and no API key or published rate limit was found. [Terms](https://francearchives.gouv.fr/fr/open_data)
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** Per a FranceArchives/Logilab presentation (SWIB 2023), an RDF dump modelled in RiC-O is published at https://data-dump.francearchives.gouv.fr/rdf/ (refreshed about every six months, roughly 400 million triples) and loaded into the SPARQL endpoint. FranceArchives is the French aggregator for the Archives Portal Europe. Search terms: arménien, Arménie, réfugiés arméniens, Office des réfugiés arméniens; overlaps with OFPRA and departmental archives (Bouches-du-Rhône).

### Hispana

*Hispana – Directorio nacional de recursos digitales* · <https://hispana.mcu.es> · ES · aggregator · `es.hispana`

Spanish national aggregator to Europeana, now titled *Directorio nacional de recursos digitales* (about 10.5 million objects from 219 repositories).

- **Access:** OAI-PMH, web pages (no authentication); metadata: dc, edm.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use unknown; attribution unknown; automated access unknown. The Aviso Legal covers general portal use by the Ministerio de Cultura and does not set an explicit licence for harvested metadata; Hispana only links to objects held by contributing institutions, whose own rights statements apply. Hispana says it acts as both OAI-PMH harvester and OAI-PMH repository, but no public base URL was found (/oai/OAIHandler returned 404). [Terms](https://hispana.mcu.es/es/contenido/aviso-legal.do)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Hispana is Spain's national aggregator to Europeana, so the practical route is Europeana's API (filter by provider 'Hispana') rather than the Hispana portal. Records link out to holding institutions (university repositories, regional digital libraries such as BVPB).

### Polona

<https://polona.pl> · PL · digital library · `pl.polona`

Polish national digital library, with materials of the Armenian community of Lviv and Polish Armenians (about 265 records for 'ormiańsk*').

- **Holdings:** Polona search API (POST /api/search-service/search/simple), 2026-11-02: 'ormiańsk*' = 265; 'Ormianie' = 229; 'Armenia' = 243; 'ormiański' = 112. A combined OR query returned 5,679 and looked unreliable, so it is not used.
- **Access:** API, web pages (no authentication); endpoint <https://polona.pl/api/search-service/search/simple>; metadata: json.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution unknown; automated access unknown. The National Library of Poland says most Polona collections are public domain and free to download and use; each record carries a rights field (e.g. 'Domena Publiczna', which allows copying, modification and commercial use while respecting authors' moral rights). The JSON search API is the site's internal, undocumented backend; no published API terms, key or rate limit were found, and the main user terms ('Regulamin usługi') are linked from the site footer. [Terms](https://www.bn.org.pl/uslugi/centrum-kompetencji/udostepnianie-zbiorow-cyfrowych/polona/)
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** Records expose language (e.g. 'ormiański'), metatype, sourceMeta (holding library, e.g. Biblioteka Jagiellońska, Patrimonium project) and rights. For Lviv Armenian community material, combine 'ormiańsk*' with 'Lwów'. Treat the internal API as unstable; throttle and identify the client. Polona content also reaches Europeana partly via Polish aggregators.

### Library of Congress

<https://www.loc.gov> · US · library · `us.loc`

One of the largest Armenian collections outside Armenia: the Armenian Rarities collection (1321 Gospel Book, 1666 Oskan Bible; about 60 digitised items), 32 manuscripts from the Armenian Patriarchate of Jerusalem, 14 catalogued manuscript titles, the American Folklife Center, maps and Prints & Photographs (late 19th–early 20th c., Genocide documentation). Chronicling America moved onto loc.gov in 2025.

- **Access:** API, IIIF, bulk download, web pages (no authentication); endpoint <https://www.loc.gov/search/?q=armenian&fo=json>; metadata: json, marc, mods, iiif.
- **Terms of use:** metadata `public-domain`; content mixed, per item; commercial use conditional; attribution unknown; automated access restricted. No API key. Published limits: loc.gov JSON/YAML API 20 requests/min (1-hour block if exceeded), image/text services 150/min, lccn.loc.gov MARCXML 30/min (72-hour block); the legal page also asks automated programs to stay at or below 10 requests/min across all machines, honour robots.txt (which disallows /search and sets Crawl-Delay 5), and warns jobs over 24 hours may be terminated. Library-created US Government works are public domain in the US and offered under CC0 internationally; collection items carry per-item rights advisories, and the Library generally does not own the rights, so users must check copyright status themselves. [Terms](https://www.loc.gov/legal/)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Use facet fa=language:armenian and the Armenian Rarities collection (https://www.loc.gov/collections/armenian-rarities/). Paginate with c=1000 and stay below the 100,000-item deep-paging limit; fetch item JSON with &fo=json&at=item,resources. Bulk MARC catalog records are offered for free download (loc.gov/cds/products/marcDist.php). Script access is currently challenged by Cloudflare, so plan a polite, rate-limited client or use bulk MARC. Overlaps: HathiTrust and Internet Archive (LoC-scanned books), DPLA (LoC is a DPLA hub).

### Digital Public Library of America

<https://dp.la> · US · aggregator · `us.dpla`

US national aggregator of library, archive and museum metadata, with monthly full dumps.

- **Access:** API, bulk download, web pages (API key required); endpoint <https://api.dp.la/v2/items>; metadata: json.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution not required; automated access API only. DPLA dedicates all aggregated metadata to the public domain under CC0; DPLA's own site content (e.g. visual assets) is CC BY, and the underlying digital objects keep each contributing institution's rights statement (edmRights). The API needs a free 32-character key, which is emailed after an HTTP POST to https://api.dp.la/v2/api_key/{email}; keys can be revoked for abuse. No official rate limit could be confirmed because the developer policy pages blocked automated reading. [Terms](https://dp.la/about/terms-conditions)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Monthly full JSON dumps are publicly listable in the S3 bucket https://dpla-provider-export.s3.amazonaws.com/ (prefixes by year/month; latest seen 2026/10/; includes per-hub files and all.json.gz). Filtering the dump locally avoids the key requirement for bulk work. Heavy overlap with HathiTrust, Smithsonian, NYPL, LoC and Internet Archive content; dedupe by isShownAt/original record id.

### HathiTrust Digital Library

<https://www.hathitrust.org> · US · digital library · `us.hathitrust`

Shared digital library of research libraries; Armenian-language volumes can be selected offline from the monthly Hathifiles (`lang=arm`).

- **Access:** API, OAI-PMH, bulk download, web pages (no authentication); endpoint <https://catalog.hathitrust.org/api/volumes/brief/oclc/{oclc}.json>; metadata: marc, json, csv.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution unknown; automated access restricted. Under the Metadata Sharing and Use Policy, metadata HathiTrust owns is shared under CC0 and may be harvested, modified and reused via Hathifiles, the Bibliographic API, OAI feed and collection exports, provided as-is. Volume access follows per-item rights codes (pd, pdus, ic, cc-*), and pdus items are public domain only in the US. Web pages block plain scripts; computational access to full text goes through the HathiTrust Research Center. [Terms](https://www.hathitrust.org/the-collection/terms-conditions/metadata-sharing-and-use-policy/)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Hathifiles: tab-delimited full file on the 1st of each month plus daily updates (about 1 GB, 17M+ rows); filter lang='arm' and keep rights code and access fields. Bibliographic API supports lookup by OCLC/LCCN/ISBN/HTID. Overlaps with Internet Archive and Google Books scans, and HathiTrust is a DPLA hub.

### Internet Archive

<https://archive.org> · US · digital library · `int.internet-archive`

Non-profit digital library with 7,467 Armenian-language items and 35,000 items matching 'armenian', including monthly *Haratch* scans and books from many libraries.

- **Holdings:** archive.org advancedsearch, 2026-11-02: language:(arm OR armenian OR hye) = 7,467 (same via Scrape API); keyword 'armenian' = 35,030; 'armenian AND licenseurl:*publicdomain*' = 683.
- **Access:** API, IIIF, bulk download, web pages (no authentication); endpoint <https://archive.org/advancedsearch.php>; metadata: json, other.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution unknown; automated access API only. Default terms limit use of collections to non-commercial, non-infringing or fair use and bar copying collections offsite without permission, but an item's declared licence (licenseurl/rights metadata) overrides the default. The Archive gives no guarantee of copyright status, so users carry the risk. Read APIs (advanced search, Scrape API, metadata API) need no key; no numeric rate limit was found. [Terms](https://archive.org/about/terms.php)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Use the Scrape API (https://archive.org/services/search/v1/scrape, cursor paging) for bulk ids, then /metadata/{id}. Language values are inconsistent (arm, armenian, hye, Armenian), so query all variants. Contains Haratch monthly scans (HARATCH_YYYY-MM), digitised Armenian books from many libraries, and audio. Overlaps with HathiTrust/Google scans and LoC. Per-item IIIF manifests exist via iiif.archive.org (root path returned 404; per-item paths not tested).

### Smithsonian Open Access

<https://www.si.edu/openaccess> · US · museum · `us.smithsonian`

Smithsonian Open Access: 408 Armenian-related records, mostly Smithsonian Libraries books and Folklife recordings. The Freer Gallery listed in v1 is now part of the National Museum of Asian Art (1 matching record).

- **Holdings:** Open Access API (DEMO_KEY), 2026-11-02: q='armenian' = 408 records (89 with images). By unit: Smithsonian Libraries 241, NMAH 71, Center for Folklife and Cultural Heritage 45, NMNH Anthropology 17, SAAM 7, NMNH Mineral Sciences 6, NMAAHC 4, National Museum of Asian Art (former Freer|Sackler) 1.
- **Access:** API, bulk download, web pages (API key required); endpoint <https://api.si.edu/openaccess/api/v1.0/search>; metadata: json.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution not required; automated access allowed. Open Access metadata is CC0, and media flagged CC0 (metadata_usage.access = CC0) can be reused for any purpose; records with copyright limits have CC0 metadata but no media. API keys come from api.data.gov (DEMO_KEY for testing; a 2026-11-02 check saw x-ratelimit-limit 10 on DEMO_KEY; registered keys commonly get 1,000 requests/hour per api.data.gov defaults, not confirmed on an official page). Bulk data is mirrored without rate limits. [Terms](https://www.si.edu/openaccess/devtools)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** Bulk: public S3 bucket smithsonian-open-access (us-west-2; prefixes metadata/, media/, images/, 3d/), verified listable, and the GitHub repo Smithsonian/OpenAccess (weekly JSON). Filter by unitCode and content.indexedStructured. Most hits are Smithsonian Libraries books and Folklife recordings.

### The Metropolitan Museum of Art Open Access

<https://www.metmuseum.org> · US · museum · `us.met`

Metropolitan Museum of Art Open Access: about 235 objects related to Armenia (manuscripts, textiles, metalwork).

- **Holdings:** Met Collection API v1.1 search, 2026-11-02: q='Armenia' = 235; q='armenian' = 213 (199 with images); q='Armenian' with artistOrCulture=true = 69; geoLocation=Armenia = 115. The union was not computed.
- **Access:** API, bulk download, web pages (no authentication); endpoint <https://collectionapi.metmuseum.org/public/collection/v1.1/search>; metadata: json, csv.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution not required; automated access allowed. The Open Access dataset and API data are CC0, and high-resolution images of public-domain works (isPublicDomain=true) are CC0 for any use; in-copyright works have identifying data only. No key or registration; the docs ask clients to stay under 80 requests per second. API use is subject to the Met's terms and conditions. [Terms](https://www.metmuseum.org/information/terms-and-conditions)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** The old /public/collection/v1/search was retired on 2026-10-01 (HTTP 410). Its replacement is /public/collection/v1.1/search (Elastic-backed, offset/limit paging, limit up to 500, offset+limit up to 10,000, same filters as v1). Enumerate fully via /public/collection/v1/objects or the GitHub CSV metmuseum/openaccess (CC0, last pushed 2026-10-26). Filter CSV on Culture/Country containing Armenia/Armenian. Object records link to Wikidata and ULAN.

### NYPL Digital Collections

<https://digitalcollections.nypl.org> · US · library · `us.nypl`

NYPL Digital Collections; the Repo API was deprecated on 2026-08-01 with no replacement.

- **Access:** API, bulk download, web pages (API key required); endpoint <https://api.repo.nypl.org/api/v2/items/search>; metadata: json, mods.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution unknown; automated access restricted. Repo API access needs a token obtained by sign-up and is limited to 10,000 requests per day per token; the API page now states the API is deprecated and no longer available from 2026-08-01, with no public replacement planned (the endpoint still answered 401 'Access denied' on 2026-11-02). Item-level rights statements apply (No Known U.S. Copyright Restrictions, CC0, NYPL-held copyright, Undetermined), and publicDomainOnly=true filters to cleared items. No metadata licence is stated for the API. [Terms](https://api.repo.nypl.org/)
- **Integration:** filter Armenian records with the matcher; priority 4; blocked.
- **Notes:** API is end-of-life, so do not build a pipeline on it. A CC0 snapshot of public-domain items (January 2016 release) is on GitHub NYPL-publicdomain/data-and-utilities (archived); filter it for Armenian subjects. Otherwise manual or browser-based discovery only.

### Trove

<https://trove.nla.gov.au> · AU · aggregator · `au.trove`

Australian national discovery platform documenting the Armenian diaspora in Australia: newspapers (Genocide coverage, relief efforts, *Armenia Weekly*, Sydney 1995–2010), images, maps and research reports.

- **Access:** API, web pages (API key required); endpoint <https://api.trove.nla.gov.au/v3/result>; metadata: json, other.
- **Terms of use:** metadata `custom`; content mixed, per item; commercial use conditional; attribution unknown; automated access restricted. API v3 requires a personal key under the Trove API Terms of Use; non-commercial keys are free, while commercial use needs explicit permission from the National Library of Australia. Since 2025 the NLA treats harvesting resource content (e.g. full text of digitised newspaper and journal articles) through the API, beyond descriptive metadata, as a breach unless an exemption agreement is negotiated; some researchers' keys were reportedly cancelled. A 5,000 requests/day figure circulates only in unofficial sources. [Terms](https://trove.nla.gov.au/about/create-something/using-api/trove-api-terms-use)
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** Metadata-only integration is the safe path: store Trove work/article ids and link out. robots.txt disallows /api/search/* and several paths for crawlers. GLAM Workbench Trove tools (Tim Sherratt) were archived after key cancellation, so third-party harvesters may no longer work.

## 4. Russia

Russian libraries, archives and museums. Goskatalog is already integrated; museum holdings of the Hermitage, the Museum of Ethnography and the State Historical Museum are covered through it. Most Russian state sites were unreachable from outside Russia on 2026-11-02.

### State Catalogue of the Museum Fund of the Russian Federation

*Государственный каталог Музейного фонда Российской Федерации* · <https://goskatalog.ru/portal/> · RU · registry · `ru.goskatalog`

Electronic database of the Museum Fund of the Russian Federation, distributed as the Ministry of Culture open dataset `7705851331-museum-exhibits`. This repository has processed a full Parquet export of 31.7 million records into 58,291 Armenia-related records and 86,714 review candidates, including works by Ivan Aivazovsky and holdings of the Hermitage, the Russian Museum of Ethnography and the State Historical Museum. v1 listed Goskatalog twice (sections 20.3 and 24.3).

- **Holdings:** This repository's extraction from the full Goskatalog open-data Parquet export (31,741,256 records, 2.86 GB): 58,291 Armenia-related records included plus 86,714 in review. Wikipedia cites 4,761,949 items / 3,736 museums (Nov 2024), which conflicts with the dump size; treat Wikipedia figure as unreliable.
- **Access:** bulk download, web pages (no authentication); endpoint <https://opendata.mkrf.ru/opendata/7705851331-museum-exhibits>; metadata: json, other.
- **Terms of use:** metadata `custom`; content restricted; commercial use yes; attribution required; automated access restricted. Dataset passport (Wayback capture 2025-03-13) applies the Russian federal 'Standard terms of use of open data' (2016): free reuse for commercial and non-commercial purposes without a contract, provided the source is cited, use is lawful and data are not distorted. The same passport states images are published for information only and remain museum property, so images are excluded from the open-data terms. [Terms](http://data.gov.ru/information-usage)
- **Integration:** filter Armenian records with the matcher; priority 1; integrated.
- **Notes:** goskatalog.ru and opendata.mkrf.ru reset connections from outside Russia (also via WebFetch); current availability of the dump could not be verified (Wayback shows a 404 on one item URL 2025-04-29). The Ministry described 2021 mass copying of the portal as 'hacker attacks' and blocked it, so use the bulk dump, not portal scraping. Hermitage (2,104), Russian Museum of Ethnography (2,242) and State Historical Museum (4,173) Armenian records are already inside this repository's Goskatalog extraction; Armenian Museum of Moscow is NOT a Museum Fund holder. Per-record image rights should be treated as all rights reserved by the holding museum; store links, not image copies.

### Institute of Oriental Manuscripts, Russian Academy of Sciences (IOM RAS), St Petersburg

*Институт восточных рукописей РАН* · <https://www.orientalstudies.ru/> · RU · research institute · `ru.iom-ras`

Institute of Oriental Manuscripts RAS (former Asiatic Museum) holding Armenian manuscripts including the Van collection rescued during World War I. The v1 figures (420 items, oldest dated 1188) could not be verified; the site was unreachable.

- **Access:** no online access (restricted / by agreement); metadata: other.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. Terms could not be checked: site unreachable. No IIIF or open-licence publication of Armenian mss found in search results.
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** Site may be geo-restricted or down. Retry later from another network. Printed catalogues and Manuscripta Orientalia/Pis'mennye pamyatniki articles are the likely count sources. The National Library of Russia holds a further 111 Armenian mss (per the same article) - a separate source.

### National Library of Russia

*Российская национальная библиотека* · <https://nlr.ru/> · RU · library · `ru.nlr`

National Library of Russia: Armenian manuscripts (described in K. Yuzbashyan's 2005 catalogue; 44 codices from Kamianets-Podilskyi) and a scanned alphabetical card catalogue of 64,000+ cards for Armenian-language printed books from 1623, plus catalogues of Armenian newspapers and periodicals. Manuscripts are shown through virtual exhibitions. v1 listed the card catalogue under Goskatalog by mistake.

- **Holdings:** Scanned Armenian alphabetical card catalogue of the Dept. of National Literatures: >64,000 cards for Armenian-language books and serials from 1623 (nlr.ru/e-case3/sc2.php/arman, checked 2026-11-02). Separate catalogues: Armenian newspapers (>200 titles) and Armenian periodicals from 1845 (~1,100 cards). Armenian manuscripts: exact count not stated on the online exhibition; shelfmarks 'Арм. н.с.' go to at least 51; 44 codices came from Kamianets-Podilskyi in 1891.
- **Access:** web pages (no authentication); endpoint <https://primo.nlr.ru/primo-explore/search?vid=07NLR_VU1>; metadata: html, other.
- **Terms of use:** metadata `custom`; content restricted; commercial use no; attribution required; automated access restricted. All site content, including images and text, is for personal non-commercial use only; any full or partial reuse must link to nlr.ru. A separate policy page covers intellectual property placed on the site. [Terms](https://nlr.ru/nlr_visit/RA2044/usloviya-ispolzovaniya)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** robots.txt has 'User-agent: * / Disallow: /' (only Google, Bing, Yandex etc. are allowed), so generic harvesting is disallowed. The card catalogue is images only (no structured records); OCR or manual work would be needed. Primo catalogue (07NLR_VU1) and electronic library (nlr.ru/elibrary) are the discovery layers; no public OAI-PMH or open-data export found. Vivaldi (vivaldi.nlr.ru) is a DRM reader requiring a client app.

### Russian State Library

*Российская государственная библиотека* · <https://www.rsl.ru/> · RU · library · `ru.rsl`

Russian State Library and operator of the National Electronic Library; 1.7 million digitised titles, full access only in reading rooms.

- **Access:** web pages (restricted / by agreement); endpoint <https://search.rsl.ru/>; metadata: html, marc.
- **Terms of use:** metadata `custom`; content mixed, per item; commercial use unknown; attribution required; automated access unknown. Full access to the Electronic Library is available only in RSL reading rooms; outside the library, access to protected items follows Part IV of the Civil Code (copyright), so only public-domain items are open remotely. The site footer requires a direct link to rsl.ru when its materials are used. [Terms](https://www.rsl.ru/electronic-resources/electronic-library)
- **Integration:** filter Armenian records with the matcher; priority 3; blocked.
- **Notes:** rsl.ru and search.rsl.ru time out from outside Russia; facts taken from Wayback. RSL is the operator of the NEB (rusneb.ru), so RSL digitized public-domain items also surface in NEB. No public API/OAI-PMH confirmed. Armenian-language items would need to be counted through search.rsl.ru language facets from inside Russia.

### National Electronic Library (NEB)

*Национальная электронная библиотека (НЭБ)* · <https://rusneb.ru/> · RU · aggregator · `ru.neb`

National Electronic Library, the federal aggregator of RSL, NLR and Presidential Library digital copies.

- **Access:** web pages (registration required); metadata: html.
- **Terms of use:** metadata `custom`; content mixed, per item; commercial use no; attribution unknown; automated access prohibited. NEB is a federal state information system operated by the Russian State Library. Users may use objects for personal, informational, scientific, educational and cultural purposes within Russian copyright law; in-copyright items are available only under licences with rightsholders. The agreement explicitly bans circumventing technical protection and mass automated downloading of NEB objects. [Terms](https://rusneb.ru/user-agreement/)
- **Integration:** filter Armenian records with the matcher; priority 4; blocked.
- **Notes:** rusneb.ru times out from abroad; terms read from Wayback capture 2026-04-24. Registration is optional for open items but needed for some functions; in-copyright items open only in authorised reading rooms. No public API or OAI-PMH documentation found. Aggregates RSL, NLR and Presidential Library digital copies, so expect duplicates with ru.rsl, ru.nlr and ru.prlib.

### Presidential Library named after B. N. Yeltsin

*Президентская библиотека имени Б.Н. Ельцина* · <https://www.prlib.ru/> · RU · digital library · `ru.prlib`

Presidential Library: digitised books, periodicals and archival documents; no dedicated Armenia collection was found.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content mixed, per item; commercial use unknown; attribution unknown; automated access unknown. No reuse terms page was found; the site footer states all rights are reserved by the Presidential Library. Only items free of copyright restrictions are open on the portal; others are viewable in the library and its regional e-reading rooms. [Terms](https://www.prlib.ru/)
- **Integration:** filter Armenian records with the matcher; priority 4; candidate.
- **Notes:** prlib.ru times out from abroad; footer read from Wayback capture 2026-10-24. The library publishes 'metadata standards for cultural heritage' guidance but no public API/OAI-PMH was found. Low priority unless an Armenia-specific collection is confirmed.

### State Hermitage Museum

*Государственный Эрмитаж* · <https://www.hermitagemuseum.org/> · RU · museum · `ru.hermitage`

State Hermitage Museum: Urartian and Armenian archaeology, medieval and decorative art. Its Armenia-related records are already in Goskatalog.

- **Holdings:** 2,104 Armenia-related Hermitage records already found in this repository's Goskatalog extraction (2026). Own collection site not queried (unreachable).
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access unknown. All site content (information, images, other materials) is Hermitage property protected by copyright unless marked otherwise. It is intended for personal use only; any reproduction, distribution or publication needs Hermitage permission. [Terms](https://www.hermitagemuseum.org/wps/portal/hermitage/about/about_the_site/image_usage_policy/?lng=en)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** hermitagemuseum.org and collections.hermitage.ru time out from abroad; policy read from Wayback capture 2024-09-17 (footer 1998-2024). Wayback has collections.hermitage.ru captures from 2024, so a newer collection portal exists. Use Goskatalog records and link out; do not copy images.

### Russian Museum of Ethnography

*Российский этнографический музей* · <https://ethnomuseum.ru/> · RU · museum · `ru.ethnography-museum`

Russian Museum of Ethnography: Armenian ethnographic collections, online via a KAMIS-based portal; records already in Goskatalog.

- **Holdings:** 2,242 Armenia-related REM records already in this repository's Goskatalog extraction. Online collection (collection.ethnomuseum.ru, KAMIS-based) shows 92,210 objects, 294 expeditions, 214 collectors (2026-11-02); Armenian search timed out.
- **Access:** web pages (no authentication); endpoint <https://collection.ethnomuseum.ru/entity/OBJECT>; metadata: html, json.
- **Terms of use:** metadata `custom`; content restricted; commercial use no; attribution required; automated access restricted. Site content including images and texts may be used for personal non-commercial, educational and media purposes, with a mandatory link when quoting. Quality images and publication rights for images, texts or museum branding require prior written permission from the museum. [Terms](https://ethnomuseum.ru/about/oficialnaya-informaciya/usloviya-ispolzovaniya-materialov-i-izobrazhenij-sajta/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** collection.ethnomuseum.ru robots.txt disallows /api/ (the JSON backend), HTML pages allowed; sitemaps exist (sitemap.xml, sitemap1.xml, sitemap2.xml). Metadata overlap with Goskatalog is expected to be high; use the online collection only to enrich with images/links.

### Armenian Museum of Moscow and Culture of Nations

*Армянский музей Москвы и культуры наций* · <https://www.armmuseum.ru/> · RU · media · `ru.armmuseum`

Editorial website of the non-profit 'Armkult' (Armenian Museum of Moscow and Culture of Nations): articles, a virtual exposition of about 10 video scenes and topical encyclopedia pages. There is no object catalogue, and the museum is not part of the Museum Fund.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access restricted. Site terms of ANO 'Armkult' (Center of Armenian Culture and Culture of Nations) cover viewing and posting content; they grant no reuse licence and forbid using third-party IP without the rightsholder's consent. Footer carries a copyright notice of the museum. [Terms](https://www.armmuseum.ru/terms-of-use)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** robots.txt blocks AI/ML crawlers by name (ClaudeBot, anthropic-ai, GPTBot, CCBot, Google-Extended, etc.) and disallows ?format=json and /api/. Not part of the Museum Fund, so absent from Goskatalog. Useful only as a link/reference source for Russian-language articles; do not harvest.

### Russian State Historical Archive

*Российский государственный исторический архив (РГИА)* · <https://fgurgia.ru/> · RU · archive · `ru.rgia`

Russian State Historical Archive: fund 821 (Department of Spiritual Affairs of Foreign Confessions, covering Armenian-Gregorian and Armenian-Catholic church affairs among others) and fund 880 (Lazarev material). Online KAISA finding aids.

- **Access:** web pages (registration required); endpoint <https://fgurgia.ru/type/rubricator>; metadata: html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. No site terms of use found. The online KAISA catalogue (fonds, inventories, files, name/place/subject indexes, flag for scanned sheets) is open; a personal account (login issued in person or remotely) is needed to order files, which are then consulted in the reading room. Copies are a paid service per the archive price list.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** fgurgia.ru times out from abroad; structure read from Wayback captures 2026. Site is built on InfoRost KAISA; no API/OAI found. Treat as a finding-aid source (fund/inventory-level records), not an item-level image source.

### Russian State Archive of Ancient Acts

*Российский государственный архив древних актов (РГАДА)* · <https://rgada.info/> · RU · archive · `ru.rgada`

Russian State Archive of Ancient Acts: main Lazarev family archive (cited as f. 1252) and foreign-relations fonds with Armenian affairs.

- **Access:** web pages (no authentication); endpoint <https://rgada.info/>; metadata: html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. No site terms of use found. Scanned inventories (описи) are published on the site; remote image access is offered for fond 350 (land-census and revision books) through the Rosarchiv document-access system; other documents are consulted in the reading room, and copies are ordered by e-mail as a paid service.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** rgada.info times out from abroad; read from Wayback capture 2026-10-17. Low priority for item-level integration; useful for finding-aid references (Lazarevs, Armenian merchants, 17th-18th c. Russian-Armenian relations).

### Russian State Military Historical Archive

*Российский государственный военно-исторический архив (РГВИА)* · <https://rgvia.ru/> · RU · archive · `ru.rgvia`

Russian State Military Historical Archive: Caucasus front records (1914–1917), including Armenian volunteer units.

- **Access:** web pages (restricted / by agreement); metadata: html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use unknown; attribution unknown; automated access unknown. Terms not found; site unreachable from abroad and no archived terms page located.
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** Unreachable from abroad. Part of RGVIA WWI personnel records is reportedly exposed via the Ministry of Defence portal 'Памяти героев Великой войны' (gwar.mil.ru) - not verified in this pass. Low priority.

### CyberLeninka

*КиберЛенинка* · <https://cyberleninka.ru/> · RU · digital library · `ru.cyberleninka`

Open-access repository of Russian scholarly journals, including articles on Armenian studies.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `custom`; content mixed, per item; commercial use no; attribution required; automated access prohibited. User agreement v. 24.11.2025 (operator OOO 'Iteos'): articles are provided free under Creative Commons or other open licences chosen by rightsholders, and services are for personal non-commercial use. It forbids commercial use of works, site elements or the database, and forbids bots, crawlers and scripts collecting information or metadata without prior written consent. [Terms](https://cyberleninka.ru/terms.html)
- **Integration:** filter Armenian records with the matcher; priority 4; blocked.
- **Notes:** OAI-PMH endpoint not confirmed (no Wayback captures of cyberleninka.ru/oai). Older reports say CyberLeninka feeds BASE, OpenAIRE, WorldCat via OAI-PMH, so harvesting its records through BASE/OpenAIRE (under their terms) may be the compliant route. robots.txt disallows /search, /api/, PDFs (except Googlebot).

### eLIBRARY.RU Scientific Electronic Library

*Научная электронная библиотека eLIBRARY.RU* · <https://www.elibrary.ru/> · RU · digital library · `ru.elibrary`

Largest Russian scientific electronic library; access largely by subscription.

- **Access:** web pages (registration required); metadata: html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use unknown; attribution unknown; automated access restricted. User agreement (agreement.asp) could not be retrieved: the archived URL redirects to a session page. robots.txt (Wayback 2026) disallows most dynamic pages (author, org, citation, item lists, querybox). Full texts depend on subscriptions or open-access journals.
- **Integration:** filter Armenian records with the matcher; priority 4; blocked.
- **Notes:** Unreachable from abroad. Institutional access is IP-controlled per library contracts. No public API. Low priority: overlaps with CyberLeninka for open-access Russian journals.

### Runivers

*Руниверс* · <https://runivers.ru/> · RU · digital library · `ru.runivers`

Historical digital library of Russian books and maps; Armenian content claimed in v1 was not found.

- **Access:** web pages (no authentication); endpoint <https://runivers.ru/library/>; metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content restricted; commercial use no; attribution required; automated access restricted. ANO 'Runivers' claims rights in the portal content and its selection. Materials may be used only for personal non-commercial purposes; modification, republication, copying for third parties and derivative works are forbidden, and commercial use needs prior consent. Quotes require naming the portal with a hyperlink at the start. [Terms](https://runivers.ru/about/agreements/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Active in Nov 2026 (Bitrix site). robots.txt disallows all URLs with query strings. Has a small 'datasets' section (Erlikhman countries-and-rulers table) but no API. Low priority.

### Electronic Library of Historical Documents (EBID), Russian Historical Society

*Электронная библиотека исторических документов (ЭБИД)* · <https://docs.historyrussia.org/> · RU · portal · `ru.docs-historyrussia`

Electronic Library of Historical Documents of the Russian Historical Society: republishes documents from printed collections since 1991; only 3 Armenia-related collection entries.

- **Access:** web pages (no authentication); endpoint <https://docs.historyrussia.org/ru/indexes/types/47>; metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No terms of use found on the archived pages. The project aims to give open access to historical documents published in Russia since 1991, with indexes by author, archive/fund, date, names, places and topics.
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Unreachable from abroad; read via Wayback (platform: InfoRost, version 9.0.39). No API found. Low priority.

## 5. Diaspora institutions: Europe, Middle East and Latin America

Libraries, archives, foundations and media of the Armenian diaspora. Most reserve all rights; integration depends on agreements.

### Houshamadyan – Open Digital Archive (ODA)

*Հուշամատեան* · <https://www.houshamadyan.org/> · DE · digital library · `de.houshamadyan`

Berlin-based project reconstructing Ottoman Armenian town and village life. Its Open Digital Archive (about 164 collection pages) presents family photographs, objects (clothing, metalwork, embroidery), letters, songs, lullabies, games, stories, beliefs and recipes, grouped by region (Americas, Armenia, Europe, Middle East, Turkey) plus the Arab Image Foundation, Wolfgang Kunz, Identity(ies) and Armenian-American music sections. Supported by the Calouste Gulbenkian Foundation.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access unknown. Houshamadyan e.V. reserves all rights to the site's texts, design, photos, audio and video, with a 2011 notice. Only personal, non-commercial use is allowed. Any other copying, publishing or adaptation needs prior written permission, though linking is allowed. No separate ODA licence exists, so the site-wide terms cover ODA images. [Terms](https://www.houshamadyan.org/copyright.html)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** TYPO3 CMS with static HTML pages at /oda/<region>/<collection>.html. Collection pages are image galleries with captions, and there is no API, OAI or IIIF. robots.txt does not exist (it returns the TYPO3 404 page). Images sit under fileadmin/. Item metadata would have to be scraped from captions, and the copyright terms forbid reuse without permission.

### AGBU Nubar Library

*Bibliothèque Nubar de l'UGAB* · <http://bnulibrary.org/> · FR · library · `fr.agbu-nubar`

Founded in 1928, one of the main centres of Armenian studies: 43,000 printed works, 800,000 archival documents, 1,400 periodical titles, 10,000 photographs and several hundred manuscripts. Key fonds: the Andonian collection on the Genocide, archives of the Armenian Patriarchate of Istanbul, the Armenian National Delegation and AGBU. Digitisation is in progress; only sample dossiers and galleries are online. v1 listed this library twice (sections 14 and 22.5).

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access unknown. The site footer reads '© 2016 La Bibliothèque Nubar de l'UGAB – Paris – Tous droits réservés'. No reuse licence or terms page exists, so reuse needs the library's permission. robots.txt blocks only the Joomla system folders. [Terms](http://bnulibrary.org/index.php/fr/credits)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Joomla site, HTTP only, with FR/EN pages under /index.php/fr|en/. It is static article pages with image galleries: no catalogue, API or IIIF. Calfa (calfa.fr/blog/7) has a scientific partnership with the library on Armenian OCR/HTR, which could feed future full-text output. Good candidate for direct contact about a data-sharing agreement.

### ARAM – Association for Research and Archiving of Armenian Memory

*Association pour la recherche et l'archivage de la mémoire arménienne* · <https://webaram.com/> · FR · archive · `fr.aram`

Reference Armenian archive in Marseille. It digitised the complete run of *Haratch* (22,214 issues, 1925–2009) and publishes other diaspora press (e.g. *Mshak*, 1880), 974 book records, music, posters and identity documents of Armenian refugees.

- **Holdings:** WordPress REST X-WP-Total, 2026-11-02: numerisation-presse 1,293 (digitized press batches, each a month or quarter of one title), livre 974, document 281, musique 195, portrait-expo-99 99, affiche-expo-1997 64, iconographie 21, presse 14 (newspaper titles), identite 5. Sum 2,932 records. Haratch is fully digitized: 22,214 issues, 1925–2009, about 600 GB, OCR searchable in Armenian/French, per the Haratch page.
- **Access:** API, web pages (no authentication); endpoint <https://webaram.com/wp-json/wp/v2/numerisation-presse>; metadata: json, html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access allowed. The site has no terms, licence or legal page. The Haratch page says Arpik Missakian authorized its digitization and distribution on webaram.com, but gives no reuse licence. 'allowed' rests only on robots.txt (Yoast, no Disallow) and an open WP REST API, not on any legal grant. Ask ARAM before republishing files.
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** WordPress 6.9 with WPML (FR/EN/ES/HY). Custom post types are exposed via /wp-json/wp/v2/{livre,presse,numerisation-presse,document,iconographie,identite,musique,...}, and Yoast sitemaps list every type. Each Haratch month has an online reader and a PDF download. Records hold little structured metadata (title, date, link), so parse the title strings ('TITLE – Armenian title – year – period').

### OFPRA Archives – Armenian refugee files (Nansen-era protection records)

*Office français de protection des réfugiés et apatrides (Ofpra) – portail des archives* · <https://archives.ofpra.gouv.fr/> · FR · archive · `fr.ofpra`

Digitised protection files of Russian, Armenian and Georgian refugees in France, 1924–1952, mostly from the Office arménien de Marseille: status and origin certificates, marriage and succession attestations, letters. The 10,256-document figure in v1 could not be verified.

- **Access:** web pages (registration required); metadata: html.
- **Terms of use:** metadata `unknown`; content restricted; commercial use no; attribution required; automated access restricted. The files hold personal data, so viewing nominative files needs an account that Mission Histoire staff validate, as the law requires for public archives under 100 years old with personal data. Ofpra's legal notice lets public information be reused free if it is not altered and the source and date are cited. Content with personal data or third-party rights cannot be reused without the consent of those concerned. The archive portal itself blocks automated clients with an Anubis challenge, and its robots.txt returns 403. [Terms](https://www.ofpra.gouv.fr/mentions-legales)
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** Not harvestable: the bot check (Anubis) and login stop scraping, and personal data makes item-level aggregation legally sensitive. At most, a collection-level record should point to the portal. Background and access info: https://www.ofpra.gouv.fr/en/dossier/nos-fonds-darchives/archives-en-ligne. On-site reading room in Fontenay-sous-Bois by appointment.

### Gomidas Institute

<https://www.gomidas.org/> · GB · research institute · `gb.gomidas`

Independent academic publisher of English-language books on Armenian history, the Genocide and diaspora (about 140 titles) and the *Armenian Forum On-Line* article page. Not a collection holder.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access allowed. The footer reads 'Copyright © 2026 The Gomidas Institute. All rights reserved.' No terms or licence page exists, and books are sold, not free. robots.txt allows all crawling, so 'allowed' covers crawling only, not reuse. [Terms](https://www.gomidas.org/)
- **Integration:** not a metadata source; priority 4; not applicable.
- **Notes:** Custom PHP CMS (credited to e-Works) with ID-based pages /books/show/{id} and /press/show/{id}. It returns HTTP 406 when the request has no browser Accept header. The blog is a separate WordPress site (blog.gomidas.org). Low priority: bibliographic metadata only.

### SALT Research

*Salt Araştırma* · <https://saltresearch.org/> · TR · archive · `tr.salt`

Istanbul research archive with over 2 million digitised resources, including Ottoman-era photographs and documents with Armenian content (e.g. Ottoman Bank staff portraits, the 1896 Ottoman Bank raid).

- **Access:** web pages (no authentication); endpoint <https://archives.saltresearch.org/>; metadata: html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use no; attribution required; automated access restricted. Digitized visual materials are provided for individual research under CC BY-NC-ND 4.0: credit the creator or licensor as the record states, no commercial use, no derivatives. Commercial use, and documents viewable only on Salt's on-site WiFi, need a request to salt.research@saltonline.org. The DSpace host's robots.txt sets Content-Signal 'ai-train=no, use=reference' as a reservation of rights under EU DSM Article 4. [Terms](https://saltresearch.org/discovery/custom/90GARANTI_INST-90SALT_VU1/html/salt/info_rights_en.html)
- **Integration:** filter Armenian records with the matcher; priority 3; candidate.
- **Notes:** Two platforms: an Ex Libris Primo VE discovery layer (vid 90GARANTI_INST:90SALT_VU1; robots disallows search, Crawl-delay 10) and a DSpace repository (archives.saltresearch.org/handle/123456789/...) behind a Cloudflare challenge. DSpace OAI-PMH (/oai/request) could not be checked because of the block. SALT is a Flickr Commons partner, so the Flickr API may be a cleaner route for its photo subset. A formal data request is advisable.

### Haigazian University – Armenian Diaspora Research Center (ADRC)

<https://www.haigazian.edu.lb/research/armenian-diaspora-rc/> · LB · research institute · `lb.haigazian-adrc`

Armenian Diaspora Research Center of Haigazian University (since 2012). Its outputs and the full *Haigazian Armenological Review* (from 1970; 1,253 items) are in the university DSpace repository.

- **Holdings:** DSpace 7 repository haigrepository.haigazian.edu.lb, discover API, 2026-11-02: Haigazian Armenological Review community 1,204 items plus ADRC community 49 = 1,253. Also HU Press 26 and Conference Proceedings 47. Whole repository 1,536 items, of which 910 match 'armenian'.
- **Access:** OAI-PMH, API, web pages (no authentication); endpoint <https://haigrepository.haigazian.edu.lb/server/oai/request>; metadata: dc, qdc, mods, mets, marc, rdf.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access allowed. No licence was found. Repository records have no dc.rights field, and the university site could not be loaded. robots.txt blocks only /search, admin and submit paths, and OAI-PMH is public. Ask Haigazian before reusing PDFs.
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** The main site returned 403/504 (Cloudflare) on 2026-11-02, while the repository was reachable. DSpace 7: REST at /server/api, OAI formats oai_dc, qdc, mods, mets, marc, rdf, didl, ore, xoai, dim, etdms, uketd_dc. Metadata is thin (author, date, title, URI, DOI) and some abstracts hold template placeholders. HAR volume PDFs are large (vol. 1 about 110 MB).

### Foundation for Culture and Heritage of Polish Armenians

*Fundacja Kultury i Dziedzictwa Ormian Polskich* · <https://dziedzictwo.ormianie.pl/> · PL · foundation · `pl.ormianie`

Foundation for Culture and Heritage of Polish Armenians: Virtual Archive of Polish Armenians (metrical books, cemeteries, manuscripts, old prints, periodicals, photographs, paintings, liturgical objects) and Wiki.Ormianie (1,826 biographies).

- **Holdings:** The count is wiki.ormianie.pl articles (biographies of Polish Armenians): 1,826 articles and 2,612 images per the MediaWiki siteinfo API, 2026-11-02. The Virtual Archive (archiwum.ormianie.pl) publishes no totals. It has sections for metrical-book search, cemeteries, manuscripts and unindexed metrical books, old prints, newspapers and periodicals, books and articles, photos, paintings and liturgical objects. The foundation's fonds are also listed on szukajwarchiwach.gov.pl (JS-rendered, not counted).
- **Access:** API, web pages (no authentication); endpoint <https://wiki.ormianie.pl/api.php>; metadata: json, html.
- **Terms of use:** metadata `CC-BY-SA-3.0`; content mixed, per item; commercial use conditional; attribution required; automated access unknown. The wiki (Wiki.Ormianie) declares CC BY-SA 3.0, so reuse, including commercial, is fine with attribution and share-alike. The Virtual Archive shows only '© Fundacja Kultury i Dziedzictwa Ormian Polskich 2023' with no licence, so treat its scans as all rights reserved. The licence code and commercial value given here apply to the wiki only. [Terms](https://wiki.ormianie.pl/api.php?action=query&meta=siteinfo&siprop=rightsinfo&format=json)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** The ecosystem under ormianie.pl: dziedzictwo (foundation), archiwum (Virtual Archive of Polish Armenians, a PHP app with search pages ksiegi.php and archiwuma.php), wiki (MediaWiki 1.24.1, open api.php), skarbnica (museum exhibition, Warsaw, Świętojerska 12) and ordynariat (Armenian Catholic ordinariate). The archive is also on szukajwarchiwach.gov.pl and the Centrum Archiwistyki Społecznej database (cas.org.pl). Digitization was funded by MKiDN 'Zasoby cyfrowe' and MSWiA. Metrical books carry genealogical personal data.

### Lepsiushaus Potsdam

<https://www.lepsiushaus.de/> · DE · research institute · `de.lepsiushaus`

Research centre in Potsdam holding a copy of the Johannes Lepsius Archive. The online edition of German Foreign Office documents on the Genocide is armenocide.net (W. and S. Gust), not a Lepsiushaus product.

- **Access:** no online access (restricted / by agreement); metadata: other.
- **Terms of use:** metadata `all-rights-reserved`; content restricted; commercial use no; attribution unknown; automated access unknown. German copyright applies. Copying, editing or distributing beyond legal limits needs the author's written consent, and downloads are for private, non-commercial use only. The archive can be visited by appointment, and single sources can be supplied digitally on request by NC number. [Terms](https://www.lepsiushaus.de/impressum)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Webflow site (cdn.prod.website-files.com) with a cookie consent banner. No catalogue, API or digital edition online. Use as a collection-level reference record only. Candidate for a cooperation request, e.g. digitized Lepsius journals.

### Calouste Gulbenkian Foundation – Armenian Communities Department

*Fundação Calouste Gulbenkian* · <https://gulbenkian.pt/armenian-communities/> · PT · foundation · `pt.gulbenkian`

Major funder of Armenian heritage projects (Houshamadyan, Haratch digitisation, Matenadaran catalogue platform, Mekhitarist press online, Calfa). The Armenian Communities Department is in Lisbon, not Paris as v1 stated. The Gulbenkian Museum holds 4 Armenian illuminated manuscripts.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution required; automated access unknown. Site content is IP-protected and for personal use only, with no commercial use. Non-commercial reuse must clearly cite the source with a link, mark changes and make no derivatives. Archive images, video and documents may not be reproduced without written authorization, which may carry fees. Bots are not addressed, though robots.txt allows crawling. [Terms](https://gulbenkian.pt/termos-de-utilizacao/)
- **Integration:** not a metadata source; priority 4; not applicable.
- **Notes:** WordPress multisite under gulbenkian.pt with Yoast sitemaps per sub-site (EN and HY pages). Useful as a cross-reference: grant lists could seed provenance or 'funded-by' links in the registry. Not a harvest target.

### Diario Armenia

<https://www.diarioarmenia.org.ar/> · AR · media · `ar.diario-armenia`

Spanish-language Armenian daily founded in 1931 in Buenos Aires. The website holds about 12,700 articles from October 2014 onward; historical issues are not digitised online.

- **Holdings:** WordPress REST /wp-json/wp/v2/posts X-WP-Total = 12,698 on 2026-11-02. The oldest online post is dated 2014-10-24. No digitized back-issue archive (1931–2014) was found online; print records reportedly sit with the Daghlian Library, Buenos Aires (ANCA news).
- **Access:** API, web pages (no authentication); endpoint <https://www.diarioarmenia.org.ar/wp-json/wp/v2/posts>; metadata: json, html.
- **Terms of use:** metadata `custom`; content all rights reserved; commercial use conditional; attribution required; automated access unknown. The two statements conflict. The site footer allows reproduction if the source is named with a link. The terms page (written for the mobile app) reserves all IP and bars copying or distribution without prior written consent. Bots are not addressed, and robots.txt blocks only /wp-admin/. Link-back citation is the minimum; get written consent for bulk or commercial reuse. [Terms](https://www.diarioarmenia.org.ar/terminos-y-condiciones/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** WordPress (theme 'Armenia2020', by Fenix Design). REST API and RSS (/rss) are open, but bare curl gets 403: send a browser User-Agent. Content is contemporary news, so it is useful for community events, not heritage objects. Consider metadata-only links.

### Centre for Armenian Studies, National University of Rosario (Cátedra Armenia)

*Centro de Estudios Armenios – Cátedra Armenia, Universidad Nacional de Rosario* · <https://catedrarmenia-cea-unr.com.ar/> · AR · research institute · `ar.cea-unr`

Academic centre for Armenian studies at the National University of Rosario (Cátedra Armenia since 2007, CEA since 2021). Not a collection holder.

- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No terms, copyright notice or licence was found. The site is a client-side app with no server-rendered content.
- **Integration:** not a metadata source; priority 4; not applicable.
- **Notes:** React/Vite single-page app: index.html is an empty shell, and the JS bundle holds no content, which is probably loaded at runtime. For UNR Armenian-studies output, harvest RepHip (https://rephip.unr.edu.ar/server/api, DSpace 7) by query or collection instead. Low priority.

## 6. Diaspora institutions: North America

Museums, libraries, oral history and photo archives in the United States and Canada.

### Armenian Museum of America

<https://www.armenianmuseum.org/> · US · museum · `us.armenian-museum`

Watertown museum with 25,000+ artifacts (religious objects, inscribed rugs, folk costumes, metalwork, paintings, embroideries, about 5,000 coins, illuminated manuscripts), the Mesrob G. Boyajian Library (30,000+ titles), a sound archive of about 3,000 78 rpm discs and a new oral history project. Objects are shown only on curated pages.

- **Holdings:** Collection page (checked 2026-11-02): over 25,000 artifacts (~5,000 coins, 3,000+ textiles, 180 inscribed rugs); less than 5% on display. Separately: Mesrob G. Boyajian Library 30,000+ titles; Sound Archive ~3,000 discs of early Armenian recordings.
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access prohibited. Terms of Service (Termageddon policy) say all site content is the museum's or third parties' property, all rights reserved. They expressly forbid robots, spiders, or other automated means to access, monitor, or copy site material. No image-licensing or open-access policy is published. [Terms](https://www.armenianmuseum.org/terms-of-service)
- **Integration:** harvest all records; priority 3; blocked.
- **Notes:** Squarespace site with no searchable online collection database: objects are shown only on curated category pages. Library OPAC is Follett Destiny on a bare IP: http://207.180.166.147:8080 (no Z39.50/SRU checked). robots.txt only blocks /config, /search and /api, but the ToS ban on automated access governs. Integration needs a permission or data-sharing agreement.

### Project SAVE Armenian Photograph Archives (Project Save Photograph Archive)

<https://www.projectsave.org/> · US · archive · `us.project-save`

Leading Armenian photograph archive (founded 1975): 150,000+ photographs from the 1860s, about 19% digitised. Collections include the Missionary Collection (Near East Relief, 1900–1920), the Jack Torosian Collection (1,361 photos of Soviet Armenia 1923–1973, 744 online) and Ottoman-era albums (Abdullah Frères, Pascal Sébah).

- **Holdings:** Homepage (2026-11-02): 150,000+ photographs from the 1860s to the present. The licensing page says 19% of the physical collection is digitized; online record count unknown because the catalogue blocks scripted access. Digital Commonwealth holds 224 Project SAVE items (API count 2026-11-02).
- **Access:** web pages (no authentication); endpoint <https://projectsave.catalogaccess.com/>; metadata: html.
- **Terms of use:** metadata `custom`; content all rights reserved; commercial use conditional; attribution required; automated access restricted. Images are licensed for a fee, per project, only for the uses on the invoice. Licensees may not crop or alter images without approval and must credit Project SAVE and the collection. The terms forbid using images, captions, keywords or other metadata for machine learning/AI or person-identification technology. [Terms](https://www.projectsave.org/licensing)
- **Integration:** harvest all records; priority 3; blocked.
- **Notes:** The homepage is Squarespace; its robots.txt disallows / for AI crawlers (ClaudeBot, GPTBot, CCBot, etc.). The catalogue is a hosted collections portal (fields Objects/Photos/Archives/Library/People/Search Terms, likely PastPerfect-style; vendor unverified). Its robots.txt disallows /api/, and it returned HTTP 403 to curl and WebFetch. Easiest harvestable subset: Digital Commonwealth (BPL) collection commonwealth:cr56n7883 via its JSON API/OAI (rights 'not evaluated', licence 'contact host'). A selection also appears in USC Shoah Foundation IWitness. Needs a partnership.

### NAASR Edward and Helen Mardigian Library (National Association for Armenian Studies and Research)

<https://naasr.org/pages/mardigian-library> · US · library · `us.naasr`

NAASR Mardigian Library: 39,000+ books, periodicals and documents back to the 1600s, including the Bournoutian collection and personal papers.

- **Holdings:** Library page (2026-11-02): over 39,000 books, pamphlets, periodicals and documents, mainly Armenian and English, back to the 1600s. Includes the 3,000+ title Bournoutian collection and personal papers (Derounian, Guerguerian, Vertanes, etc.).
- **Access:** web pages (no authentication); endpoint <https://naasr.follettdestiny.com/>; metadata: marc, html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. No library-specific terms of use or reuse policy was found. The site footer gives only a NAASR copyright notice. The robots.txt is a Shopify storefront file that allows crawling.
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Catalogue is Follett Destiny (naasr.follettdestiny.com portal). Search results report WorldCat participation from 2025 and records in the National Library of Armenia's catalogue, a possible easier harvest route; not verified. Digitized yearbooks are listed in a Dropbox .docx; the Derounian finding aid is a Dropbox PDF. 'Library Treasures' blog posts. The site is a Shopify storefront whose robots.txt carries shopping-agent text, which was ignored. NAASR holds a perpetual USC Shoah Foundation VHA subscription for on-site use.

### Krikor and Clara Zohrab Information Center

<https://zohrabcenter.org/> · US · library · `us.zohrab-center`

Library and archive of the Eastern Diocese in New York: 15,000+ catalogued volumes, maps, hmayils and personal papers.

- **Holdings:** Online catalogue covers 15,000+ volumes (catalogue launch notice); other Center posts claim 20,000+ to 50,000+ items in total. Special collections include the Vava Sarkis Khachaturian papers, Arshile Gorky material, maps/atlases, and hmayils.
- **Access:** web pages (no authentication); endpoint <https://dac.bibliovation.com/>; metadata: marc, html.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access restricted. No terms of use or reproduction policy was found on the Center's website. Digital copies are by request to the coordinator, and holdings do not circulate.
- **Integration:** harvest all records; priority 3; blocked.
- **Notes:** Part of the Eastern Diocese of the Armenian Church of America, at St. Vartan Cathedral, NYC. The catalogue runs on Bibliovation (Koha-based); its robots.txt disallows all crawling (User-agent: * Disallow: /), and a Koha OAI path was not found. The old catalogue domain zohrabcentercatalog.com no longer resolves. WordPress site with a 'Digitized Books' post category. Ask for a MARC export.

### USC Dornsife Institute of Armenian Studies

<https://dornsife.usc.edu/armenian/> · US · research institute · `us.usc-dornsife-ias`

USC Institute of Armenian Studies digitisation projects: the Armen Aroyan Collection (about 400 videotapes of ~100 journeys to Western Armenia, nearly half online since July 2025), diasporan ephemera (Armine Koundakjian and others) and Armenian Radio Hour recordings. Materials are published through USC Digital Library (Orange Logic).

- **Holdings:** Approximate. A July 2025 Institute news item says the Armen Aroyan Collection has ~400 videotapes (trips 1988-2016, ~100 tours, ~1,470 participants), and 'nearly half' is on USC Digital Library. No item counts exist for the ephemera or Armenian Radio Hour projects.
- **Access:** web pages (no authentication); endpoint <https://digitallibrary.usc.edu/API/SEO/v1.0/SitemapIndex?Name=sitemapindex.xml.gz>; metadata: html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution required; automated access restricted. USC Digital Library gives copyright and use information per item in its Rights fields. Reuse beyond fair use needs the copyright owner's written permission, and commercial use of copyrighted works needs a request. USC Libraries expects users to cite the collection and credit USC Libraries; publication may need a fee-based license. [Terms](https://digitallibrary.usc.edu/C.aspx?VP3=CMS3&VF=AboutUs_VForm)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Aroyan collection page: https://digitallibrary.usc.edu/CS.aspx?VP3=SearchResult&VBID=2A3BXZLVXCTWQ&PN=1&WS=PackagePres. The page is a JS-heavy Orange Logic UI. No public OAI-PMH or IIIF was found; robots.txt sets Crawl-delay 30 and disallows /Share/ and thumbnail utilities. A sitemap index is exposed (gzip). Ask USC Libraries (specol@usc.edu) or armenian@usc.edu for a metadata export.

### USC Shoah Foundation Visual History Archive

<https://vha.usc.edu/> · US · archive · `us.usc-shoah-vha`

Visual History Archive with two Armenian collections: the Armenian Film Foundation (J. Michael Hagopian, 333 interviews) and the Richard G. Hovannisian collection (636 of 1,000+ interviews indexed by 2023).

- **Holdings:** Two Armenian collections, summed. Armenian Film Foundation (J. Michael Hagopian): 333 audio-visual interviews with 380+ people (sfi.usc.edu/content/armenian-genocide). Richard G. Hovannisian collection: 636 interviews available (SFI obituary, July 2023) out of 1,000+. Whole VHA: 60,394 testimonies.
- **Access:** web pages (registration required); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content restricted; commercial use no; attribution unknown; automated access prohibited. VHA website terms (revised 2017-11-01) grant a limited, revocable licence for personal, educational, non-commercial use only. They ban automated scripts, scraping, framing, and systematic downloading or printing. Unauthorized copying, downloading or recording of interviews is prohibited; reuse licences go through SFIAccess (sfiaccess.usc.edu). [Terms](https://vha.usc.edu/pages/termsofuse)
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** Angular SPA with an internal, non-public API (vha.usc.edu/services/api/...). The terms text loads from vha.usc.edu/assets/html/termsofuse.html. VHA Online (free registration) shows metadata for all testimonies but full video for only ~4,430. Full access is at ~204 subscribing institutions, e.g. NAASR (perpetual subscription) and AGMI Yerevan. Ingest only via a negotiated agreement; record collection-level metadata only.

### Richard G. Hovannisian Armenian Genocide Oral History Collection (formerly UCLA Armenian Genocide Oral History Project)

<https://sfi.usc.edu/collections/armenian> · US · archive · `us.ucla-armenian-oral-history`

1,000+ audio interviews recorded 1972–2000 by Richard Hovannisian and UCLA students. Since 2018 the collection is held and served by the USC Shoah Foundation; UCLA no longer holds it.

- **Holdings:** 1,000+ audio interviews recorded 1972-2000 by Hovannisian and his UCLA students, mostly in California. Per the SFI obituary (2023-07-13), 636 are available in the USC Shoah Foundation VHA. Language is mostly Armenian, up to ~20% English, a few Turkish/Spanish.
- **Access:** web pages (registration required); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content restricted; commercial use no; attribution unknown; automated access prohibited. The collection is now served only through the USC Shoah Foundation VHA, so VHA terms apply: personal, educational, non-commercial use only. Automated scraping and downloading are banned, and copies or licences go through SFIAccess. [Terms](https://vha.usc.edu/pages/termsofuse)
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** Duplicate of us.usc-shoah-vha content: model it as a sub-collection and dedupe. In VHA Online, filter by the collection checkbox 'Richard G. Hovannisian Armenian Genocide Oral History Collection'. Collection info: https://sfi.usc.edu/content/hovannisian-collection-text.

### Columbia Armenian Oral History Archive, 1968-1977 (Oral History Archives at Columbia, Rare Book & Manuscript Library)

<https://findingaids.library.columbia.edu/archives/cul-5321412> · US · archive · `us.columbia-oral-history`

Armenian Oral History Archive, 1968–1977 (MS#1480, created by Vazken L. Parsegian): about 130–139 digitised interviews in Armenian, English and Turkish, many available on Columbia Digital Library Collections.

- **Holdings:** A 2025 Archival Science article (doi 10.1007/s10502-025-09516-7, via search) gives 139 oral histories; a Columbia RBML blog post says '130+ interviews'. Interviews are in Armenian, English and Turkish. Count not checked in the finding aid itself, which sits behind a bot challenge.
- **Access:** web pages (no authentication); metadata: ead, marc, html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution unknown; automated access restricted. Uses beyond fair use (publication, broadcast, display, derivatives) need a media permission licence. The Oral History Archives license only material whose copyright Columbia Trustees own; for other interviews, contact the narrator or estate. Scholarly use is fee-free; commercial audio was $175 per the page (via search). Item records carry US copyright or private-study notices, and some items need a Columbia login. [Terms](https://library.columbia.edu/libraries/rbml/oral-history/media-publishing.html)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** findingaids.library.columbia.edu, dlc.library.columbia.edu and clio.columbia.edu all return an Anubis proof-of-work bot challenge to scripted clients; it was not bypassed. DLC robots.txt sets Crawl-delay 10 and exposes a sitemap: https://dlc.library.columbia.edu/sitemaps/sitemap.xml.gz. Item example: https://dlc.library.columbia.edu/catalog/cul:0k6djh9xsr. Ask Columbia for an EAD/MARC export or whitelisting.

### Zoryan Institute

<https://zoryaninstitute.org/> · CA · research institute · `ca.zoryan`

Armenian Genocide Oral History Collection (about 780 interviews, ~3,000 hours) consulted on site at the Zoryan Institute & AUA Center for Oral History.

- **Holdings:** Armenian Genocide Oral History Collection: AUA library lists 780 interviews (Armenian 77%, English 22%, Turkish 1%); Zoryan cites 750+ interviews and ~3,000 hours. The downloadable catalogue (xlsx, 21 alphabetical sheets) has ~1,200 populated rows in the downloaded catalogue; rows may not equal interviews. Also Syrian-Armenian and 44-Day War oral history collections.
- **Access:** bulk download, web pages (no authentication); endpoint <https://zoryaninstitute.org/wp-content/uploads/2023/02/CATALOGUE_-Armenian-Genocide-Oral-History-Collection-1.xlsx>; metadata: other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use conditional; attribution unknown; automated access unknown. Recordings may be viewed only on site, by appointment, for research or education; they cannot be borrowed and general requesters get no copies. Direct descendants can buy a copy (US/CAD $450 per oral history). Publishing any part needs a signed Copyright Agreement with the Institute. [Terms](https://zoryaninstitute.org/oral-history/oral-history-access-policy/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Recordings are consulted at the Zoryan Institute & AUA Center for Oral History (AGBU Papazian Library, American University of Armenia, Yerevan): https://library.aua.am/ziauaoh/collections-armgen/. The catalogue xlsx (881 KB) has columns #, Last/First/Maiden Name, parents' names, Gender, Interview Date, Birth Year/Place/Region, Interview Length, Language, notes. It holds personal data on survivors; consider privacy before republishing. WordPress site.

### Armenian National Institute

<https://www.armenian-genocide.org/> · US · research institute · `us.ani`

Armenian National Institute: Genocide documents, photographs and a database of 300+ memorials in 45 countries.

- **Holdings:** Memorials database page (2026-11-02): 300+ Armenian Genocide memorials in 45 countries. Separate sample-document and photo galleries have no stated totals.
- **Access:** web pages (no authentication); metadata: html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution required; automated access restricted. ANI claims copyright in its site content and compilation. Personal use (view, download, print) needs no permission. Copying material onto other websites is prohibited. Any publication, including digital, needs a written request and an ANI authorization letter that specifies the acknowledgment; links are allowed only from non-profit educational sites. [Terms](https://www.armenian-genocide.org/copyright.html)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** Static HTML site (Armenian, Spanish, Turkish and Arabic subdomains). robots.txt blocks only specific bots. Source documents (US, German and British archival reports) may be public domain at origin, but ANI's transcriptions and images fall under its notice. Memorials database built with Rockefeller Foundation funding; good for monuments geodata after permission. No API.

### Rockefeller Archive Center - Near East Foundation records (Near East Relief)

<https://rockarch.org/> · US · archive · `us.rockefeller-ner`

Near East Foundation (Near East Relief) records at the Rockefeller Archive Center, with CC0 archival description; the related Near East Relief Historical Society Digital Museum claims 40,000+ digitised items.

- **Access:** web pages, bulk download, IIIF (no authentication); endpoint <https://github.com/RockefellerArchiveCenter/data>; metadata: ead, mets, json, html.
- **Terms of use:** metadata `CC0-1.0`; content mixed, per item; commercial use conditional; attribution not required; automated access allowed. RAC dedicates its archival description and library records (DIMES HTML and JSON) to the public domain under CC0; attribution is encouraged, not required. CC0 does not cover linked images or digital objects, whose rights vary by item and donor. Publication may need RAC and donor permission. [Terms](https://docs.rockarch.org/archival-description-license)
- **Integration:** filter Armenian records with the matcher; priority 2; candidate.
- **Notes:** DIMES catalogue: https://dimes.rockarch.org (SPA; robots allows all). The JSON API host api.rockarch.org returned 403 to curl. Bulk EAD and METS are on GitHub, updated regularly. IIIF/Mirador viewer is reported for digitized objects; not verified. No NEF collection hit was confirmed in DIMES via search. Near East Relief Historical Society Digital Museum: https://neareastrelief.org/ (neareastmuseum.com redirects there), assets on NetX (https://neareast.netx.net/portals/digital-museum/); a free account opens the full archive. Its rights policy (https://neareastrelief.org/rights-use-policy/) uses item-level rights, aims at non-commercial research/education, and grants no permissions itself.

### Armenian Studies Program, California State University, Fresno

<https://cah.fresnostate.edu/armenianstudies/> · US · research institute · `us.fresno-state`

Armenian Studies Program: an Internet Archive collection (157 items), Flickr Commons photographs, the Index of Armenian Architecture (~65 monument pages) and a program library.

- **Holdings:** Internet Archive collection csufarmenianstudies (via California Revealed): 157 items (103 images, 54 texts), API count 2026-11-02. Flickr Commons photo count not checked (API key needed). The Index of Armenian Architecture has ~65 monument pages. Program library catalogue on LibraryWorld (size not verified).
- **Access:** API, web pages (no authentication); endpoint <https://archive.org/advancedsearch.php?q=collection%3Acsufarmenianstudies&fl%5B%5D=identifier&rows=200&output=json>; metadata: json, html.
- **Terms of use:** metadata `unknown`; content mixed, per item; commercial use conditional; attribution unknown; automated access allowed. Flickr Commons images are marked 'no known copyright restrictions'. On Internet Archive, 30 items carry the Public Domain Mark 1.0; others are copyrighted by donors (e.g., Richard A. Hagopian, the Chookasezian family) and online access does not permit further reproduction. [Terms](https://cah.fresnostate.edu/armenianstudies/resources/library/index.html)
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Index of Armenian Architecture: static HTML pages by building type at /armenianstudies/resources/architecture/; no data download. The IAA miniatures page links to the Hamburg Index of Armenian Art. Flickr: http://www.flickr.com/photos/145517650@N04/albums. Library OPAC: https://opac.libraryworld.com/library/ASP. A George Injajikian papers finding aid PDF is on the site. No Fresno State CONTENTdm found (fresnostate.contentdm.oclc.org gives 403/notfound). Best harvest route: Internet Archive metadata API, plus the Flickr API with a key.

### Hairenik Association - Hairenik Digital Archives (Hairenik / Armenian Weekly)

*Հայրենիք* · <https://hairenik.com/> · US · media · `us.hairenik`

Hairenik Digital Archives: *Hairenik* (from 1899) and *Armenian Weekly* (1969–2025) runs, searchable, with paid PDF access.

- **Access:** web pages (restricted / by agreement); endpoint <https://hairenik.hisystems.net/>; metadata: html, other.
- **Terms of use:** metadata `unknown`; content restricted; commercial use conditional; attribution required; automated access unknown. Searching is open, but opening PDFs needs a paid subscription ($35/year individual; a $500/year multiuser licence was reported in 2020). The archive's disclaimer lets single images be reused if Hairenik Digital Archives is credited with a link. Reusing multiple images, or any commercial use, needs prior Hairenik Association approval. [Terms](https://hairenik.hisystems.net/)
- **Integration:** link / enrich only; priority 4; blocked.
- **Notes:** hairenik.org is a parked GoDaddy domain; the Association's site is hairenik.com, which sits behind Cloudflare and blocks curl. The archive is a WordPress site on hisystems.net; PDFs are delivered through Google Drive sharing to subscribers' Gmail accounts, with file prefixes AW/HW/HD. armenianweekly.com is also Cloudflare-protected (403 to curl), with metered article access. The Armenian Weekly ended print in June 2025. No API.

### The Armenian Mirror-Spectator

<https://mirrorspectator.com/> · US · media · `us.mirror-spectator`

*Armenian Mirror-Spectator* (since 1932): 14,290 web articles from 2008 and print-edition PDFs from 2009.

- **Holdings:** Archives page (2026-11-02) lists 14,290 web articles, year filter 2008-2026. Past Issues has ~86 listing pages of print-edition PDFs, from June 13, 2009 to Oct 31, 2026. No online digitized run for 1932-2008 was found.
- **Access:** web pages (no authentication); endpoint <https://mirrorspectator.com/past-issues/>; metadata: html, other.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use no; attribution unknown; automated access restricted. The site claims copyright with all rights reserved; no detailed terms of use or reuse licence was found. Recent PDF issues are linked for direct download without a stated paywall. [Terms](https://mirrorspectator.com/disclaimer/)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** WordPress; PDFs at /wp-content/uploads/YYYY/MM/Armenian-Mirror-Spectator-<date>.pdf. The site returns 403 to curl (bot protection), though WebFetch worked; respect it. Owned by Baikar Association (Watertown, MA). The paper descends from the Armenian Mirror (1932) and merged with the Spectator in 1939. Pre-2009 back issues need contact with the publisher or libraries holding microfilm.

## 7. Heritage lists, monitoring and maps

Official heritage lists and monitoring projects documenting monuments, including Armenian heritage outside Armenia.

### UNESCO Intangible Cultural Heritage

<https://ich.unesco.org> · FR · registry · `int.unesco-ich`

Armenia has **8** elements on the Representative List: Duduk and its music (2008, proclaimed 2005), Armenian cross-stones art (Khachkars, 2010), the epic *David of Sassoun* (2012), Lavash (2014), Kochari (2017), Armenian letter art (2019), Pilgrimage to the St. Thaddeus Apostle Monastery (2020, joint with Iran) and the Tradition of blacksmithing in Gyumri (2023). v1 listed only the last four.

- **Holdings:** ich.unesco.org/en/state/armenia-AM and data.unesco.org dataset ich001, 2026-11-02: 8 elements, all on the Representative List: 2008 Duduk and its music; 2010 Khachkars (cross-stone art); 2012 Daredevils of Sassoun / David of Sassoun epic; 2014 Lavash; 2017 Kochari; 2019 Armenian letter art; 2020 Pilgrimage to the St. Thaddeus Apostle Monastery (joint with Iran, countries IR+AM); 2023 Tradition of blacksmithing in Gyumri. No 2024 or 2025 inscriptions. Ongoing 2026 nominations: Tirgān/Vardavar water and rain tradition; winemaking in the Areni community.
- **Access:** API, bulk download, web pages (no authentication); endpoint <https://data.unesco.org/api/explore/v2.1/catalog/datasets/ich001/records>; metadata: json, csv.
- **Terms of use:** metadata `CC-BY-SA-4.0`; content mixed, per item; commercial use conditional; attribution required; automated access API only. The ich001 dataset on data.unesco.org (849 elements) is CC BY-SA 4.0; images and videos carry their own copyright/author fields. UNESCO's site terms (updated 2026-09-15) bar commercial use without a licence or authorisation, require citation (UNESCO, year, title, URL), prohibit bots, crawlers and bulk downloads (except ordinary search indexing), and require written permission for substantial or systematic database extraction and for AI training. ich.unesco.org robots.txt blocks AI crawlers. [Terms](https://www.unesco.org/en/terms-use)
- **Integration:** harvest all records; priority 2; planned.
- **Notes:** Use the data.unesco.org Opendatasoft API (where=search("Armenia") or filter countries contains 'AM'), not scraping ich.unesco.org. Fields: inscription_year, type_acronym (RL/USL/GSP), countries, concepts, whc_sites links, media. Duduk was first proclaimed a Masterpiece in 2005 and integrated into the Representative List in 2008.

### UNESCO World Heritage Centre

<https://whc.unesco.org> · FR · registry · `int.unesco-whc`

Armenia has **3** World Heritage properties: Monasteries of Haghpat and Sanahin (1996, extended 2000); Cathedral and Churches of Echmiatsin and the Archaeological Site of Zvartnots (one property, 2000); Monastery of Geghard and the Upper Azat Valley (2000). Armenian heritage inscribed elsewhere: Archaeological Site of Ani (Türkiye, 2016) and Armenian Monastic Ensembles of Iran (2008).

- **Holdings:** data.unesco.org dataset whc001, 2026-11-02: Armenia has 3 properties: Monasteries of Haghpat and Sanahin (id 777, 1996, extended 2000); Cathedral and Churches of Echmiatsin and the Archaeological Site of Zvartnots (id 1011, 2000); Monastery of Geghard and the Upper Azat Valley (id 960, 2000). Armenian heritage abroad: Archaeological Site of Ani (Türkiye, id 1518, 2016); Armenian Monastic Ensembles of Iran (id 1262, 2008). Tentative List not checked on whc.unesco.org (403); press reports say about 8 entries after 2025 additions.
- **Access:** API, bulk download, web pages (no authentication); endpoint <https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/records>; metadata: json, csv.
- **Terms of use:** metadata `CC-BY-SA-4.0`; content mixed, per item; commercial use conditional; attribution required; automated access API only. The World Heritage List dataset whc001 (1,273 properties, 6 UN languages, coordinates, components) is published on data.unesco.org under CC BY-SA 4.0; images carry author/copyright fields. whc.unesco.org itself returned 403 to scripts and WebFetch, and UNESCO terms (2026-09-15) prohibit bots, bulk downloads and systematic database extraction without written authorisation, so use the licensed dataset. [Terms](https://www.unesco.org/en/terms-use)
- **Integration:** harvest all records; priority 2; planned.
- **Notes:** Query whc001 with where=search("Armenia") or search("Armenian"): 9 hits, including non-Armenian sites mentioning Armenians (Bethlehem, Derbent, Lviv, Mtskheta), so filter manually. The legacy XML feed whc.unesco.org/en/list/xml/ returned 403. No Tentative List dataset is on data.unesco.org (whc002/whc003 do not exist).

### Hrant Dink Foundation – Turkey Cultural Heritage Map

*Hrant Dink Vakfı – Türkiye Kültür Varlıkları Haritası* · <https://turkiyekulturvarliklari.hrantdink.org/> · TR · foundation · `tr.hrant-dink`

The Turkey Cultural Heritage Map documents 9,727 sites, of which 4,485 are Armenian (2,413 churches, 1,325 schools, 434 monasteries, 177 cemeteries). The foundation also produces the KarDes multicultural memory guide app.

- **Holdings:** GeoJSON from POST /a/mapPois (empty query), 2026-11-02: 9,727 points in total. By community: Armenian (Ermeni) 4,485, Greek (Rum) 4,225, Syriac 683, Jewish 314, other 20. Armenian by type: 2,413 churches, 1,325 schools, 434 monasteries, 177 cemeteries, 74 chapels, 48 orphanages, 9 hospitals, 4 fountains, 1 other.
- **Access:** API, web pages (no authentication); endpoint <https://turkiyekulturvarliklari.hrantdink.org/a/mapPois>; metadata: json.
- **Terms of use:** metadata `unknown`; content unknown; commercial use unknown; attribution unknown; automated access unknown. Neither the map nor hrantdink.org shows a terms of use, copyright notice or data licence (only a privacy policy on the main site). The Foundation's printed reports carry '© Hrant Dink Vakfı Yayınları'. The project was funded by the EU and the Foundation. Ask the Foundation before bulk reuse.
- **Integration:** harvest all records; priority 2; candidate.
- **Notes:** Data loads via JS (Leaflet). The undocumented internal endpoints are: POST /a/mapPois (form fields query, type), which returns a GeoJSON FeatureCollection (id, poi_name, ethnicity_name, building_type_name, image, icon, lon/lat); GET /a/getPoisFilters, which returns filter vocabularies (cities, ethnicity, denomination, building type); and /a/exportPois (Excel export button). Behind Cloudflare, with ACAO '*'. There is no robots.txt (unknown paths fall back to the app shell). Detail-page URLs were not resolved. Expect Turkish place names and types, and map ethnicity 'Ermeni' to Armenian.

### Monument Watch – Monitoring the Cultural Heritage of Artsakh

<https://monumentwatch.org/> · AM · portal · `int.monument-watch`

Monitoring of Armenian cultural heritage in Artsakh: 2,785 historical places, 1,378 under active monitoring, alerts and fact sheets.

- **Holdings:** The homepage counters (read 2026-11-02 via fetch) show 2,785 'Historical Places' and 1,378 under 'Active Monitoring'. WP REST X-WP-Total, 2026-11-02: wpsl_stores (map and monument records) 1,162, alerts 780, facts_and_details 139, monitoring_watch 53, posts 377, media 5,651. The REST totals may mix the Polylang language versions.
- **Access:** API, web pages (no authentication); endpoint <https://monumentwatch.org/wp-json/wp/v2/wpsl_stores>; metadata: json, html.
- **Terms of use:** metadata `all-rights-reserved`; content all rights reserved; commercial use unknown; attribution required; automated access unknown. Per the site footer, all published material belongs to the team and is protected by international copyright. Copying is not allowed without a link to the source section. Photos may not be used with the logo removed or cropped. There is no open licence or separate terms page, and robots.txt allows all. [Terms](https://monumentwatch.org/en/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** WordPress with Polylang (EN/HY/RU), WP Store Locator (map, wpsl/v1 and wpsl_stores CPT), CPT UI (alerts, monitoring_watch, facts_and_details), Wordfence and GiveWP. Bare curl gets 406: send a browser Accept header. Monument coordinates are likely in wpsl store meta (not checked). Content is politically sensitive, so keep provenance and attribution prominent.

### Caucasus Heritage Watch

<https://caucasusheritage.cornell.edu/> · US · research institute · `us.caucasus-heritage-watch`

Cornell/Purdue satellite monitoring of heritage in and around Nagorno-Karabakh: 605 sites in a public ArcGIS layer, with periodic monitoring reports.

- **Holdings:** The public ArcGIS layer 'Heritage Site Conditions' (NKHeritageList_M14_viewlayer_14Jan2026/FeatureServer/2) returned 605 features (returnCountOnly) on 2026-11-02. The homepage reports 500+ sites monitored, 18 destroyed, 17 damaged and 40 threatened (last update Oct 2026). The WordPress heritage_site type has 31 impacted-site pages.
- **Access:** API, web pages (no authentication); endpoint <https://services1.arcgis.com/mLNdQKiKsj5Z5YMN/arcgis/rest/services/NKHeritageList_M14_viewlayer_14Jan2026/FeatureServer/2/query>; metadata: json.
- **Terms of use:** metadata `unknown`; content all rights reserved; commercial use unknown; attribution unknown; automated access unknown. The site footer reads '© 2026 Caucasus Heritage Watch, Cornell University. All rights reserved.' The public ArcGIS dashboard, web map and feature layers have empty licenseInfo and accessInformation, so data reuse terms are unstated. Ask CHW (chw@cornell.edu) before redistributing; reports and maps should be cited. [Terms](https://caucasusheritage.cornell.edu/)
- **Integration:** harvest all records; priority 3; candidate.
- **Notes:** WordPress 7.1 with JetEngine. The heritage_site CPT is at /index.php?rest_route=/wp/v2/heritage_site. The live dashboard is ArcGIS Online item aab447a0d64f4eba84504e213953b748 (web map 3c75983928d04827b122ded28f967ab3). Feature layer fields: Site_No, Province_pre2020_ARM, Province_post2020_AZE, Type, Name, Begin_age, End_age, Current_Site_Status, Current_Monitoring_Status, Initial_Impact_Season, Initial_impact_mission_no. The query endpoint supports f=json/geojson. Monitoring reports (#9, Oct 2026) and StoryMaps are linked from the site. Related book: Heritage Forensics (Cornell UP).

## 8. Reference and authority data

Open knowledge graphs, media repositories and gazetteers used to link and enrich records.

### Wikidata

<https://www.wikidata.org> · US · registry · `int.wikidata`

Open knowledge graph: 22,025 items with a heritage designation in Armenia, plus identifiers linking to Europeana, Commons, GeoNames, VIAF, Getty and Pleiades.

- **Holdings:** WDQS, 2026-11-02: items with heritage designation (P1435) and country Armenia (P17=Q399) = 22,025; all items with P17=Q399 = 57,827.
- **Access:** SPARQL, API, bulk download, web pages (no authentication); endpoint <https://query.wikidata.org/sparql>; metadata: rdf, json.
- **Terms of use:** metadata `CC0-1.0`; content open licences; commercial use yes; attribution not required; automated access allowed. Structured data is CC0 (Wikimedia Terms of Use apply to the service). WDQS limits: 60-second query timeout, 60 seconds of processing per minute per User-Agent+IP, 5 parallel queries per IP, 30 failed queries per minute; over-limit clients get 429 with Retry-After and may be banned. A descriptive User-Agent is required by the Wikimedia User-Agent policy. [Terms](https://www.wikidata.org/wiki/Wikidata:Licensing)
- **Integration:** harvest all records; priority 1; integrated.
- **Notes:** Integrated 2026-11-02 with scripts/harvest_wikidata.py and the portal connector `wikidata_parquet`; the MVP publication holds a sample of the first 120 items by QID (run with --limit to extend it to the full selection of 22,025). Scholarly articles were split into a separate graph; query-scholarly.wikidata.org/sparql answered on 2026-11-02, while heritage items stay on the main endpoint. Full JSON/RDF dumps at https://dumps.wikimedia.org/wikidatawiki/entities/ (verified). Good hub for cross-ids (Europeana, Commons categories, GeoNames, VIAF, Getty, Pleiades).

### Wikimedia Commons

<https://commons.wikimedia.org> · US · digital library · `int.wikimedia-commons`

Free media repository: 158,323 files from Wiki Loves Monuments Armenia (2013–2026) plus categories for Armenian manuscripts and monuments.

- **Holdings:** Commons API categoryinfo, 2026-11-02: sum of 'Images from Wiki Loves Monuments YYYY in Armenia' subcategories (2013-2026) = 158,323 files (largest: 2017 34,824; 2015 26,520; 2013 23,879). Category:Cultural heritage monuments in Armenia has 1,554 direct files; Category:Armenian manuscripts 243 direct files (subcategories not summed).
- **Access:** API, bulk download, web pages (no authentication); endpoint <https://commons.wikimedia.org/w/api.php>; metadata: json, rdf.
- **Terms of use:** metadata `CC-BY-SA-4.0`; content open licences; commercial use yes; attribution required; automated access allowed. Every file carries its own free licence (CC BY-SA, CC BY, CC0, public domain), and Commons only accepts licences that allow commercial reuse; attribution/share-alike follow the file's licence. Text on file description pages is CC BY-SA 4.0, while Structured Data on Commons is CC0. API needs no key; follow the User-Agent policy and API etiquette (serial requests, maxlag). [Terms](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
- **Integration:** link / enrich only; priority 2; candidate.
- **Notes:** WLM Armenia 2015 and 2017 categories are labelled 'Armenia & Nagorno-Karabakh', so filter by monument id. Read licence/author per file via prop=imageinfo&iiprop=extmetadata. Pair with Wikidata heritage items (P1435, P17=Q399) and their Commons category (P373). Dumps of Commons wikitext and SDC exist on dumps.wikimedia.org.

### GeoNames

<https://www.geonames.org> · CH · registry · `int.geonames`

Geographical gazetteer: 10,517 features for Armenia, with Armenian-script alternate names.

- **Holdings:** GeoNames statistics page, 2026-11-02: Armenia (AM) = 10,517 features. Country dump AM.zip is 1,170,204 bytes, last modified 2026-11-02.
- **Access:** API, bulk download, web pages (no authentication); endpoint <https://download.geonames.org/export/dump/AM.zip>; metadata: csv, rdf, json.
- **Terms of use:** metadata `CC-BY-4.0`; content open licences; commercial use yes; attribution required; automated access allowed. GeoNames data is free under a CC BY licence (credit GeoNames with a link), commercial use allowed, provided as-is. Daily dumps need no account; the web services need a registered 'username' and allow 10,000 credits per day and 1,000 per hour per application (the shared 'demo' account was exhausted during the 2026-11-02 check). Premium SLA services exist. [Terms](https://www.geonames.org/export/)
- **Integration:** link / enrich only; priority 2; candidate.
- **Notes:** Use AM.zip plus alternateNamesV2 for Armenian-script names; historical Armenian places outside Armenia need TR/IR/GE/AZ dumps. Link via Wikidata P1566.

### Getty Vocabularies (AAT, TGN, ULAN)

<https://www.getty.edu/research-conservation/tools-databases/vocabularies/> · US · authority · `int.getty-vocab`

Getty AAT, TGN and ULAN vocabularies (TGN: 295 places under Armenia, tgn:7006651).

- **Holdings:** vocab.getty.edu SPARQL, 2026-11-02: TGN places with gvp:broaderPartitiveExtended tgn:7006651 (Hayastan, nation) = 295; separate historical-region record tgn:7004538 'Armenia'.
- **Access:** SPARQL, bulk download, web pages (no authentication); endpoint <https://vocab.getty.edu/sparql>; metadata: rdf, json.
- **Terms of use:** metadata `ODC-By-1.0`; content open licences; commercial use yes; attribution required; automated access allowed. AAT, TGN and ULAN are released by the J. Paul Getty Trust under ODC-By 1.0 with a suggested credit line. Full LOD downloads in N-Triples are refreshed monthly; XML and relational-table releases were discontinued (final archives drawn 2026-01-30). No key; no published rate limit. [Terms](https://www.getty.edu/research/tools/vocabularies/obtain/download.html)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** The tgn:7006657 id belongs to Belarus; Armenia (nation) is tgn:7006651. Use the prefix-declared /sparql endpoint (/sparql.json with unprefixed queries returned 500). CONA and IA are not available as LOD. /page/tgn/ links now redirect to the legacy getty.edu/vow display.

### Pleiades

<https://pleiades.stoa.org> · US · authority · `int.pleiades`

Gazetteer of ancient places covering ancient and late-antique Armenia (Artaxata, Tigranocerta, provinces).

- **Access:** bulk download, web pages (no authentication); endpoint <https://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz>; metadata: json, csv, rdf.
- **Terms of use:** metadata `CC-BY-3.0`; content open licences; commercial use yes; attribution required; automated access restricted. Pleiades content (copyright Ancient World Mapping Center and ISAW) may be shared and remixed under CC BY 3.0. Use the daily dumps for bulk work: robots.txt sets Crawl-delay 3 and disallows several paths, and site search is behind a bot challenge. [Terms](https://pleiades.stoa.org/help/conditions)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Latest JSON dump about 136 MB (Last-Modified 2026-11-02, HEAD verified). Also GitHub isawnyu/pleiades.datasets (pushed 2026-10-30; GitHub reports licence NOASSERTION, but the site states CC BY 3.0). Covers ancient and late-antique Armenia (Artaxata, Tigranocerta, provinces). Link via Wikidata P1584.

### VIAF: The Virtual International Authority File

<https://viaf.org> · US · authority · `int.viaf`

Virtual International Authority File for personal and corporate names.

- **Access:** API, bulk download, web pages (no authentication); endpoint <https://viaf.org/viaf/search>; metadata: marc, rdf, json, other.
- **Terms of use:** metadata `ODC-By-1.0`; content open licences; commercial use yes; attribution required; automated access restricted. VIAF data is published by OCLC under the Open Data Commons Attribution License (ODC-By), with a recommended attribution statement (canonical VIAF URIs acceptable where the full statement is not feasible); the data page was last updated 2024-09-04. In January 2025 OCLC rebuilt the VIAF web and API interfaces: JSON search output changed and RDF now needs an Accept header, and reported errors raised governance concerns. Current dump availability and rate limits were not verifiable because the site blocked automated reads. [Terms](https://viaf.org/viaf/data)
- **Integration:** link / enrich only; priority 4; candidate.
- **Notes:** Search with CQL, e.g. local.personalNames all "..."; prefer resolving ids from Wikidata (P214) instead of bulk VIAF calls. Client libraries (viapy, viafr) needed 2025 fixes, so test parsers against the current JSON.

## Appendix

### Open Data Armenia

<https://data.opendata.am> is the Open Data Armenia community portal. It is the publication target for datasets produced by this project, including the Goskatalog extraction ([armenian-and-armenia-related-artwork-in-russian-museums](https://data.opendata.am/dataset/armenian-and-armenia-related-artwork-in-russian-museums)). It is not evaluated here as an independent source.

### Keeping this document current

The machine-readable registry [`data/sources.csv`](../data/sources.csv) is the reference for access and terms. Re-check the `terms_url` of a source and update `verified_at` before integrating it, and run `python3 scripts/sources.py` after any change.
