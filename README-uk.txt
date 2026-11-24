# Gemini Sport XML filter for Prom.ua

This repository downloads the Russian supplier feed and keeps offers whose `<vendor>` field is exactly `Gemini` or `Gemini Sport` (case-insensitive).

Source:
`https://geminisport.ua/price/drop-ru.xml`

Output:
`gemini-sport-ru.xml`

## Setup

1. Create a **public** repository on GitHub, for example `gemini-sport-feed`.
2. Upload these files and folders to the repository root, keeping `.github/workflows/refresh-feed.yml` in that exact location.
3. In the repository, open **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**, then save.
4. Open the **Actions** tab, select **Refresh Gemini Sport XML**, and click **Run workflow** once.
5. Wait for the run to finish successfully. The workflow will then refresh the file every 4 hours.
6. Copy the stable raw-file URL:
   `https://raw.githubusercontent.com/YOUR-GITHUB-USERNAME/gemini-sport-feed/main/gemini-sport-ru.xml`
   Replace `YOUR-GITHUB-USERNAME` with your GitHub username and `gemini-sport-feed` if you chose a different repository name.
7. Add that URL as the supplier XML import link in Prom.ua.

## Important

- The repository must be public for the free GitHub Pages/hosting-free approach described here; the raw XML URL will be publicly accessible.
- GitHub scheduled runs can be delayed. The workflow also supports manual runs from Actions.
- The filter uses the supplier's `<vendor>` field, not words in the product title.
- In the supplied `drop-ru.xml`, the exact `<vendor>` value `Gemini Sport` appeared on 1,042 offers; exact `Gemini` did not appear as a separate vendor value in the inspected file.
- Prices and stock values are copied unchanged from the supplier feed. No markup is applied.
- The script refuses to publish an empty result or an invalid XML file.
