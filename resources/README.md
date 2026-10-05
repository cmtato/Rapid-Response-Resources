# Original resource files

This folder holds every resource in its original, editable form: the PowerPoint, Word, and Excel files as they were authored. Nothing here is generated, and nothing here has been reformatted for the web.

If you just want to read or use the materials, the [resources site](https://cmtato.github.io/Rapid-Response-Resources/) opens them in the browser, and the [main README](../README.md) has a table that maps them to the Illumina and Nanopore workflows. Come here when you want the editable originals.

## Folders

| Folder | Contents |
|---|---|
| `protocols/` | Master protocol documents, bench worksheets with reagent calculations, and catalog/reagent reference lists |
| `slides-and-worksheets/` | Training slide decks with their accompanying activity and reference worksheets |
| `playbook/` | Templates and trackers for planning and running a training workshop |
| `gen-epi/` | The genomic epidemiology train-the-trainer toolkit and its accompanying slide decks |

## How files are named

Filenames carry their place in the training sequence and the platform they apply to:

- A leading code gives the file's place in its sequence: `DL01` through `DL10` for the dry lab (data analysis) modules, `PB00` through `PB16` for the playbook, `GE00` onward for the genomic epidemiology materials, and a bare number for the wet lab protocol steps. Protocol numbers follow the corresponding protocols.io entry, so they are not consecutive. `AppendixA` marks reference material rather than a step.
- `-I` means Illumina, `-O` means Nanopore (ONT), and no platform marker means the file applies to both.

For example, `DL05-O_QC and interpretation slides for ONT.pptx` is dry lab module 5, for Nanopore, and `04-I_RNA Library Prep Worksheet Template - NEB kit.xlsx` is protocol step 4 for Illumina using the NEB kit.

## Downloading

GitHub cannot download a single folder, so to get everything use the green **Code** button on the [repository home page](https://github.com/cmtato/Rapid-Response-Resources) and choose **Download ZIP** (about 130 MB), then open the `resources` folder inside. To download one file, open it here on GitHub and use the download button, or use the **Download original** button on that resource's page on the site.

## If you edit a file here

The website does not update on its own. The browser-viewable copies in `docs/` are generated from this folder, so after changing a file here, someone needs to re-run the conversion described in [`tools/README.md`](../tools/README.md). Until then the site keeps serving the previous version.
