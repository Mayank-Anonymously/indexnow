import type { NextApiRequest, NextApiResponse } from "next";
import path from "path";
import fs from "fs";
import { exec } from "child_process";

type LinkEntry = {
  link: string[];
  name: string;
  email: string;
  url?: string;
  message?: string;
  repeat?: number;
};

// JSON storage
const filePath = path.join(process.cwd(), "data", "links.json");

// List of Python scripts to trigger
const pythonScripts = [
  "C:\\Users\\HP\\Desktop\\auto-submit-bot\\elektropractticum.nl\\submit_form_json.py",
  "C:\\Users\\HP\\Desktop\\auto-submit-bot\\elektropractticum.nl\\kunden.py",

  // "C:\\Users\\HP\\Desktop\\auto-submit-bot\\elektropractticum.nl\\thepages_show.py",
];

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === "GET") {
    try {
      const fileData = fs.readFileSync(filePath, "utf8");
      const links: LinkEntry[] = JSON.parse(fileData);
      return res.status(200).json(links);
    } catch (error) {
      return res.status(500).json({ error: "Failed to read data file" });
    }
  }

  if (req.method === "POST") {
    const {
      links,
      name,
      email,
      url,
      message,
      repeat = 1,
    } = req.body as {
      links: string[];
      name: string;
      email: string;
      url?: string;
      message?: string;
      repeat?: number;
    };

    if (!links || !links.length || !name || !email) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    try {
      // Read and update links.json
      const fileData = fs.readFileSync(filePath, "utf8");
      const allLinks: LinkEntry[] = JSON.parse(fileData);

      const newEntry: LinkEntry = {
        link: links,
        name,
        email,
        url,
        message,
        repeat,
      };
      allLinks.push(newEntry);

      fs.writeFileSync(filePath, JSON.stringify(allLinks, null, 2));

      // 🔁 Run all Python scripts
      pythonScripts.forEach((scriptPath) => {
        exec(`python "${scriptPath}" ${repeat}`, (error, stdout, stderr) => {
          if (error) {
            console.error(
              `❌ Error running ${path.basename(scriptPath)}:`,
              error.message
            );
          }
          if (stderr) {
            console.error(
              `⚠️ Stderr from ${path.basename(scriptPath)}:`,
              stderr
            );
          }
          console.log(`✅ Output from ${path.basename(scriptPath)}:\n`, stdout);
        });
      });

      return res.status(201).json({
        message: "Links added and all scrapers triggered",
        entry: newEntry,
      });
    } catch (error) {
      return res.status(500).json({ error: "Failed to update data file" });
    }
  }

  return res.status(405).json({ error: "Method not allowed" });
}
