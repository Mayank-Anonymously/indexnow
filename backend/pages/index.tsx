import { useState } from "react";

export default function Home() {
  const [linksText, setLinksText] = useState("");
  const [repeatCount, setRepeatCount] = useState(1);
  const [response, setResponse] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!linksText.trim()) {
      setResponse("⚠️ Please enter at least one link.");
      return;
    }

    setLoading(true);
    setResponse(null);

    const linksArray: string[] = [];
    const regex = /href=["'](.*?)["']/gi;
    let match;
    while ((match = regex.exec(linksText))) {
      const url = match[1].trim();

      var test = `<p><a href='${url}'>${url}</a></p>`;
      if (test) linksArray.push(test); // ✅ each link stored separately
    }
    console.log(linksArray);
    if (linksArray.length === 0) {
      setResponse("⚠️ No valid links found.");
      setLoading(false);
      return;
    }

    try {
      const res = await fetch("/api/links", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          links: linksArray,
          name: "jessy",
          email: "jessy@gamail.com",
          url: "https://unitedddd.com",
          message: "",
          repeat: repeatCount,
        }),
      });

      const result = await res.json();
      if (res.ok) {
        setResponse(`✅ Added ${linksArray.length} links successfully`);
        setLinksText("");
      } else {
        setResponse(`❌ Failed: ${result.error}`);
      }
    } catch (error) {
      setResponse("❌ Failed to add links");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>📌 Add Links for Scraper</h1>

      <textarea
        rows={8}
        placeholder="Paste one link per line..."
        value={linksText}
        onChange={(e) => setLinksText(e.target.value)}
        style={{
          width: "100%",
          padding: "0.75rem",
          borderRadius: "8px",
          border: "1px solid #ccc",
          fontSize: "1rem",
          marginBottom: "1rem",
        }}
      />

      <div style={{ marginBottom: "1rem" }}>
        <label style={{ marginRight: "0.5rem", fontWeight: "bold" }}>
          🔁 Repeat count:
        </label>
        <input
          type="number"
          min={1}
          value={repeatCount}
          onChange={(e) => setRepeatCount(Number(e.target.value))}
          style={{
            width: "80px",
            padding: "0.5rem",
            borderRadius: "6px",
            border: "1px solid #ccc",
          }}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          padding: "0.75rem 1.5rem",
          background: "#0070f3",
          color: "white",
          border: "none",
          borderRadius: "8px",
          cursor: "pointer",
        }}
      >
        {loading ? "Submitting..." : "Submit Links"}
      </button>

      {response && (
        <p style={{ marginTop: "1rem", fontWeight: "bold" }}>{response}</p>
      )}
    </div>
  );
}
// import { useState } from "react";

// export default function Home() {
//   const [linksText, setLinksText] = useState("");
//   const [repeatCount, setRepeatCount] = useState(1);
//   const [response, setResponse] = useState<string | null>(null);
//   const [loading, setLoading] = useState(false);

//   const handleSubmit = async () => {
//     if (!linksText.trim()) {
//       setResponse("⚠️ Please enter at least one link.");
//       return;
//     }

//     setLoading(true);
//     setResponse(null);

//     // ✅ Accept plain URLs line-by-line
//     const linksArray: string[] = linksText
//       .split("\n")
//       .map((line) => line.trim())
//       .filter((line) => line.startsWith("http"))
//       .map((url) => `<a href=${url}>${url}</a>`);
//     // .map((url) => `${url}`); // Convert to HTML format

//     if (linksArray.length === 0) {
//       setResponse("⚠️ No valid links found.");
//       setLoading(false);
//       return;
//     }

//     try {
//       const res = await fetch("/api/links", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({
//           links: linksArray,
//           name: "jessy",
//           email: "jessy@gamail.com",
//           url: "https://unitedddd.com",
//           message: "",
//           repeat: repeatCount,
//         }),
//       });

//       const result = await res.json();
//       if (res.ok) {
//         setResponse(`✅ Added ${linksArray.length} links successfully`);
//         setLinksText("");
//       } else {
//         setResponse(`❌ Failed: ${result.error}`);
//       }
//     } catch (error) {
//       setResponse("❌ Failed to add links");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div
//       style={{
//         padding: "2rem",
//         fontFamily: "sans-serif",
//         maxWidth: "600px",
//         margin: "0 auto",
//       }}
//     >
//       <h1>📌 Submit Plain Links for Scraping</h1>

//       <textarea
//         rows={8}
//         placeholder="Paste one link per line (e.g. https://example.com/page)"
//         value={linksText}
//         onChange={(e) => setLinksText(e.target.value)}
//         style={{
//           width: "100%",
//           padding: "0.75rem",
//           borderRadius: "8px",
//           border: "1px solid #ccc",
//           fontSize: "1rem",
//           marginBottom: "1rem",
//         }}
//       />

//       <div style={{ marginBottom: "1rem" }}>
//         <label style={{ marginRight: "0.5rem", fontWeight: "bold" }}>
//           🔁 Repeat count:
//         </label>
//         <input
//           type="number"
//           min={1}
//           value={repeatCount}
//           onChange={(e) => setRepeatCount(Number(e.target.value))}
//           style={{
//             width: "80px",
//             padding: "0.5rem",
//             borderRadius: "6px",
//             border: "1px solid #ccc",
//           }}
//         />
//       </div>

//       <button
//         onClick={handleSubmit}
//         disabled={loading}
//         style={{
//           padding: "0.75rem 1.5rem",
//           background: "#0070f3",
//           color: "white",
//           border: "none",
//           borderRadius: "8px",
//           cursor: "pointer",
//         }}
//       >
//         {loading ? "Submitting..." : "Submit Links"}
//       </button>

//       {response && (
//         <p
//           style={{
//             marginTop: "1rem",
//             fontWeight: "bold",
//             color: response.startsWith("✅") ? "green" : "red",
//           }}
//         >
//           {response}
//         </p>
//       )}
//     </div>
//   );
// }
