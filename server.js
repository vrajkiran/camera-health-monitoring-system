import { createReadStream, existsSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(join(fileURLToPath(new URL(".", import.meta.url)), "dist"));
const port = Number(process.env.PORT || 3010);

const types = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".woff": "font/woff"
};

createServer((request, response) => {
  const requestedPath = decodeURIComponent(new URL(request.url, `http://localhost:${port}`).pathname);
  let filePath = resolve(join(root, requestedPath.replace(/^(\.\.[/\])+/, "")));

  // Strict containment check: ensure requested file is inside dist/
  if (!filePath.startsWith(root + sep) && filePath !== root) {
    response.statusCode = 403;
    response.end("Forbidden");
    return;
  }

  if (requestedPath === "/" || !existsSync(filePath)) {
    filePath = join(root, "index.html");
  }

  // Security headers
  response.setHeader("X-Content-Type-Options", "nosniff");
  response.setHeader("X-Frame-Options", "SAMEORIGIN");
  response.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
  response.setHeader("Content-Type", types[extname(filePath)] || "application/octet-stream");

  createReadStream(filePath)
    .on("error", () => {
      response.statusCode = 404;
      response.end("Not found");
    })
    .pipe(response);
}).listen(port, "127.0.0.1", () => {
  console.log(`CC Camera Health Monitor running at http://127.0.0.1:${port}`);
});
