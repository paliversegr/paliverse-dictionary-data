# PaliVerse Dictionary data

Data files for **Dictionary View** on [PaliVerse](https://www.paliverse.org), built from the
[Digital Pāḷi Dictionary](https://www.dpdict.net/) (DPD) by Bodhirasa Bhikkhu.

In Dictionary View a reader hovers over or taps a Pāli word and sees its headword, grammar and meaning.
The website keeps a light extract of DPD: only the word forms that occur in each collection of the
Chaṭṭha Saṅgāyana (CST) root texts, with their headwords and the deconstructor results for joined words.

## How it works

1. Once a day a scheduled job (`.github/workflows/build.yml`) asks whether DPD has a new release.
2. For a new release it downloads the DPD database, reads the CST texts, and builds one file per collection
   (`build_all.py`, `build_data.py`, `sets.json`).
3. `check_build.py` refuses the build if a file is missing or if the share of words found falls.
4. The files and a `manifest.json` (version, checksums, word counts) are published as a release with the
   same tag as the DPD release.
5. The PaliVerse Dictionary plugin on paliverse.org reads the manifest of the latest release once a day and
   installs new data by itself.

To build a release by hand: **Actions → Build dictionary data → Run workflow**.

## Files

| File | Collection |
|---|---|
| `dn.json`, `mn.json`, `sn.json`, `an.json` | Dīgha, Majjhima, Saṃyutta and Aṅguttara Nikāya |
| `kn1.json` … `kn5.json` | Khuddaka Nikāya, in five parts |
| `vin.json` | Vinaya Piṭaka |
| `abh.json` | Abhidhamma Piṭaka |

Format: `{"v": DPD release, "forms": {form: [headword ids, grammar, deconstructor]}, "hw": {id: entry}}`.

## Licence

The data is an extract of the Digital Pāḷi Dictionary, © Bodhirasa Bhikkhu, licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), and is shared here under the same
licence.

The source texts are the Chaṭṭha Saṅgāyana edition published by the Vipassana Research Institute
([tipitaka-xml](https://github.com/VipassanaTech/tipitaka-xml)).

PaliVerse is a project of the Centre for Study and Practice of Theravada, a civic non-profit company in Athens, Greece.
