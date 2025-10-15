import type { NextApiRequest, NextApiResponse } from "next";
import fs from "fs";
import path from "path";

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { url } = req.body;
  if (!url) {
    return res.status(400).json({ error: "Missing URL" });
  }

  // Generate a unique ID
  const id = Date.now().toString();

  const filePath = path.join(process.cwd(), "data", "redirects.json");
  const data = fs.existsSync(filePath)
    ? JSON.parse(fs.readFileSync(filePath, "utf8"))
    : {};

  data[id] = url;

//   fs.writeFileSync(filePath, JSON.stringify(data, null, 2));

  // Return the redirect URL
  const redirectUrl = `https://indexnow-sooty.vercel.app/redirects/${id}`;
  res.status(201).json({ id, redirectUrl });
}
