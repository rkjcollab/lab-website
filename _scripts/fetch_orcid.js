const fs = require("fs");
const path = require("path");
const axios = require("axios");
const yaml = require("js-yaml");

// Load ORCID ID from _data/orcid.yaml
const orcidYamlPath = path.join(__dirname, "../_data/orcid.yaml");
let orcidId;
try {
  const orcidYaml = yaml.load(fs.readFileSync(orcidYamlPath, "utf8"));
  orcidId = orcidYaml.orcid || orcidYaml.id;
  if (!orcidId) throw new Error("No ORCID ID found in orcid.yaml");
} catch (err) {
  console.error("❌ Failed to read _data/orcid.yaml:", err.message);
  process.exit(1);
}

// Fetch works from ORCID public API
const apiUrl = `https://pub.orcid.org/v3.0/${orcidId}/works`;
axios.get(apiUrl, { headers: { Accept: "application/json" } })
  .then(async (res) => {
    const groups = res.data.group || [];
    const entries = [];

    for (const group of groups) {
      const summary = group["work-summary"]?.[0];
      if (!summary) continue;

      const title = summary.title?.title?.value || "Untitled";
      const id = summary["external-ids"]?.["external-id"]?.[0]?.["external-id-value"] || summary["put-code"];
      const date = summary["publication-date"]
        ? `${summary["publication-date"].year?.value || "0000"}-${summary["publication-date"].month?.value || "01"}-${summary["publication-date"].day?.value || "01"}`
        : "0000-01-01";

      entries.push({
        id: `orcid:${id}`,
        title: title,
        date: date,
        type: "paper",
        link: `https://orcid.org/${orcidId}`
      });
    }

    // Write to _data/sources.yaml
    const sourcesYamlPath = path.join(__dirname, "../_data/sources.yaml");
    const yamlStr = yaml.dump(entries, { lineWidth: 1000 });
    fs.writeFileSync(sourcesYamlPath, yamlStr, "utf8");
    console.log(`✅ Saved ${entries.length} works to _data/sources.yaml`);
  })
  .catch((err) => {
    console.error("❌ Error fetching ORCID works:", err.message);
  });
