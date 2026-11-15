# Blog

Hugo blog hosted on Render: https://blog-kcnz.onrender.com/.

Render builds `main` automatically with `bash scripts/render-build.sh` and serves
the generated `public` directory. The build pins Hugo Extended 0.128.0, matching
the previous production build. `render.yaml` records the service configuration.

For local development, install Hugo Extended 0.128.0 and Go 1.23.2 or newer, then
run `hugo server`. To check a production build, run `hugo --gc --minify`.

## Custom domain cutover

The existing domain is `blog.cameronengineer.com`. In Cloudflare, change the `blog`
CNAME target to `blog-kcnz.onrender.com` (DNS only while Render verifies the
domain and provisions TLS). Verify the domain in Render, then set `HUGO_BASEURL`
to `https://blog.cameronengineer.com/` in the service environment and redeploy.
Until then, Render builds use its own address so links and assets work there.

GitHub Pages can be disabled after the custom domain serves the Render site.
