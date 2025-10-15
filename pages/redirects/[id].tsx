import { GetServerSideProps } from "next";
import fs from "fs";
import path from "path";

export default function RedirectPage() {
  return <div>Redirecting...</div>;
}

export const getServerSideProps: GetServerSideProps = async (context) => {
  const { id } = context.params!;

  // Read the redirects JSON
  const filePath = path.join(process.cwd(), "data", "redirects.json");
  const jsonData = fs.readFileSync(filePath, "utf8");
  const targetMap: Record<string, string> = JSON.parse(jsonData);

  const targetUrl = targetMap[id as string];
  if (!targetUrl) {
    return { notFound: true };
  }

  return {
    redirect: {
      destination: targetUrl,
      permanent: false,
    },
  };
};
