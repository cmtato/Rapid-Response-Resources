# Original resource files

This folder holds every resource in its original, editable form: the PowerPoint, Word, and Excel files as they were authored. Nothing here is generated, and nothing here has been reformatted for the web.

If you just want to read or use the materials, the [resources site](https://cmtato.github.io/Rapid-Response-Resources/) opens them in the browser, and the [main README](../README.md) has a table that maps them to the Illumina and Nanopore workflows. Come here when you want the editable originals.

## Folders

| Folder | Contents |
|---|---|
| `protocols/` | Master protocol documents and the bench worksheets with reagent calculations |
| `slides/` | Training slide decks |
| `worksheets/` | Activity and reference worksheets used alongside the decks |
| `playbook/` | Playbook materials (to be added) |

## How files are named

Filenames carry their place in the training sequence and the platform they apply to:

- A leading number or `DL` (Dry Lab) code gives the module order: `1. through 8.` for the wet lab sequence, `DL1.` through `DL10.` for the dry lab (data analysis) sequence.
- `-I` means Illumina, `-O` means Nanopore (ONT), and no platform marker means the file applies to both.

For example, `DL5-O_QC and interpretation slides for ONT.pptx` is dry lab module 5, for Nanopore.

## Downloading

GitHub cannot download a single folder, so to get everything use the green **Code** button on the [repository home page](https://github.com/cmtato/Rapid-Response-Resources) and choose **Download ZIP** (about 130 MB), then open the `resources` folder inside. To download one file, open it here on GitHub and use the download button, or use the **Download original** button on that resource's page on the site.

## If you edit a file here

The website does not update on its own. The browser-viewable copies in `docs/` are generated from this folder, so after changing a file here, someone needs to re-run the conversion described in [`tools/README.md`](../tools/README.md). Until then the site keeps serving the previous version.
