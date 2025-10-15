// import type { NextApiRequest, NextApiResponse } from "next";
// import path from "path";
// import fs from "fs";
// import axios from "axios";

// type LinkEntry = {
//   link: string[];
//   name: string;
//   email: string;
//   url?: string;
//   message?: string;
//   repeat?: number;
// };

// // JSON storage
// const filePath = path.join(process.cwd(), "data", "other-links.json");

// // List of ping services
// const PING_SERVICES = [
//   "https://pingomatic.com/ping/", // example, you can add more
// ];

// // Helper: Ping URLs
// async function pingUrls(urls: string[]) {
//   for (const url of urls) {
//     for (const pingEndpoint of PING_SERVICES) {
//       try {
//         await axios.get(pingEndpoint, { params: { url } });
//         console.log(`✅ Pinged ${url} via ${pingEndpoint}`);
//       } catch (err: any) {
//         console.error(
//           `❌ Failed to ping ${url} via ${pingEndpoint}:`,
//           err.message || err
//         );
//       }
//     }
//     // small delay between URLs
//     await new Promise((resolve) => setTimeout(resolve, 1500));
//   }
// }

// export default async function handler(
//   req: NextApiRequest,
//   res: NextApiResponse
// ) {
//   if (req.method === "GET") {
//     try {
//       const fileData = fs.readFileSync(filePath, "utf8");
//       const links: LinkEntry[] = JSON.parse(fileData);
//       return res.status(200).json(links);
//     } catch (error) {
//       return res.status(500).json({ error: "Failed to read data file" });
//     }
//   }

//   if (req.method === "POST") {
//     const {
//       links,
//       name,
//       email,
//       url,
//       message,
//       repeat = 1,
//     } = req.body as {
//       links: string[];
//       name: string;
//       email: string;
//       url?: string;
//       message?: string;
//       repeat?: number;
//     };

//     if (!links || !links.length || !name || !email) {
//       return res.status(400).json({ error: "Missing required fields" });
//     }

//     try {
//       // Read and update JSON file
//       const fileData = fs.readFileSync(filePath, "utf8");
//       const allLinks: LinkEntry[] = JSON.parse(fileData);

//       const newEntry: LinkEntry = {
//         link: links,
//         name,
//         email,
//         url,
//         message,
//         repeat,
//       };
//       allLinks.push(newEntry);
//       fs.writeFileSync(filePath, JSON.stringify(allLinks, null, 2));

//       // Ping all URLs
//       await pingUrls(newEntry.link);

//       return res.status(201).json({
//         message: "Links added and pinged to social discovery services",
//         entry: newEntry,
//       });
//     } catch (error) {
//       console.error("❌ POST handler error:", error);
//       return res
//         .status(500)
//         .json({ error: "Failed to update data file or ping URLs" });
//     }
//   }

//   return res.status(405).json({ error: "Method not allowed" });
// }
// pages/api/submit-link.ts
import type { NextApiRequest, NextApiResponse } from "next";
import fs from "fs";
import path from "path";
import axios from "axios";

type SubmitRequest = {
  url: string; // the URL to be indexed
};

const HOST = "indexnow-nine.vercel.app"; // your domain
const API_KEY = "8b8a855443ae443ebd36a6626fb45bf5"; // your IndexNow key
const REDIRECTS_DIR = path.join(process.cwd(), "public", "redirects");

// Ensure redirects directory exists
if (!fs.existsSync(REDIRECTS_DIR))
  fs.mkdirSync(REDIRECTS_DIR, { recursive: true });

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST")
    return res.status(405).json({ error: "Method not allowed" });

  const { url } = req.body as SubmitRequest;
  if (!url) return res.status(400).json({ error: "Missing URL" });

  try {
    // 1️⃣ Create a unique redirect page
    const fileName = `redirect-${Date.now()}.html`;
    const filePath = path.join(REDIRECTS_DIR, fileName);

    const redirectHtml = `<html>
      <head>
        <meta http-equiv="refresh" content="0; URL='${url}'" />
      </head>
      <body>Redirecting to <a href="${url}">${url}</a></body>
    </html>`;

    fs.writeFileSync(filePath, redirectHtml, "utf8");

    const hostedUrl = `https://${HOST}/redirects/${fileName}`;

    // 2️⃣ Verify API key file exists
    const keyFilePath = path.join(process.cwd(), "public", `${API_KEY}.txt`);
    if (!fs.existsSync(keyFilePath))
      return res.status(500).json({ error: "API key file missing in /public" });

    // 3️⃣ Submit redirect page to IndexNow
    const payload = {
      host: HOST,
      key: API_KEY,
      keyLocation: `https://${HOST}/${API_KEY}.txt`,
      urlList: [hostedUrl],
    };

    const response = await axios.post(
      "https://www.bing.com/indexnow",
      payload,
      {
        headers: { "Content-Type": "application/json" },
        timeout: 15000,
      }
    );

    return res.status(200).json({
      message: "URL hosted and submitted to IndexNow successfully",
      hostedUrl,
      indexNowResponse: response.data,
    });
  } catch (error: any) {
    console.error("❌ IndexNow submission error:", error.message || error);
    return res.status(500).json({ error: "Failed to submit URL to IndexNow" });
  }
}
