# Security at the boundary

> Read when: the change takes anything from outside the process (steps 3 and 6 of SKILL.md).
"Outside" means: a file or archive someone else made, a network response, an environment variable, a CLI argument,
a request body, a path or name a user typed, a queue message, another machine's output.

Every row is a question to answer with a line of code or a test, not with an opinion. A "yes, and here is the line"
goes in the report; a "no" is a finding.

| Boundary | Ask | Typical failure | Check |
|---|---|---|---|
| **Archives and paths** | Is every entry name / joined path proven to stay inside the target folder, before anything is written? | `tar -xf` after looking only at the first entry; `path.join(base, userInput)` with `../` | A test that unpacks an archive with a `../` or absolute entry in the middle and sees it refused |
| **Verify, then use** | Does signature / checksum verification happen **before** unpack, execute or install, on the exact bytes used? | Unpacking first and verifying later; verifying one file and running another | A test where the signature is wrong and nothing was written or run |
| **Remote code** | Is anything fetched and then executed (`curl … \| bash`, `eval`, dynamic `require`)? If yes, is the source pinned (key pin, digest) and is `-k`/`--insecure` absent? | A "trusted URL" with TLS checks off | grep the change for `\| *(ba)?sh`, `-k `, `--insecure`, `rejectUnauthorized: *false`; each hit needs a pin or a stated reason (a loopback health check is a valid reason) |
| **Shell and process** | Does any user-controlled string reach a shell? | `exec(\`cmd ${x}\`)`, `sh -c`, `shell: true` | Argument arrays only (`execFile`, `spawn` without a shell); a test with `; touch x` in the input |
| **State files** | Is every state file written atomically (temp file in the same folder, then rename), and what does a failed read return? | `writeFile` interrupted → invalid JSON → reader falls back to "empty" → replay protection or locks silently off | A test that corrupts the file and sees a loud failure, not an empty default |
| **Secrets** | Who can read the file, the env var, the log line? Does a token reach a child process or a build step that does not need it? | World-readable env files; a login token exported to every build | File mode asserted in a test (0600 / 0640); the child's env built from an allow-list |
| **Auth and sessions** | Does every state-changing route check identity, role and a CSRF guard? Is a plain-HTTP start refused or loud? | A route added without the guard; the cookie loses `Secure` over HTTP | One test per new route: no session → 401, wrong role → 403 |
| **Concurrency and replay** | Can the same command run twice, or two writers interleave? | Dead connections kept in a waiter list; nonce store lost on crash | A test for the second delivery and for a closed connection |
| **Input size and time** | Is every body, upload and loop bounded, with a timeout? | Unbounded read into memory; no request timeout | A test with an oversized input |

## When it applies

- **Tiny** change: only the rows the change touches.
- **Standard / Large**: walk the whole table once in step 3 for the boundaries the design note lists, and again over the diff in step 6.
- A change that touches none of these says so in one line in the report ("no external input").

## Rules

- A finding in code you did not touch is reported, not fixed, unless the task asks (same rule as existing debt).
- A fix starts with a test that reproduces the attack input and is seen red for that reason.
- Never put a real secret in a test; use a generated value.

## Sources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP, Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- OWASP, Cross-Site Request Forgery Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP, OS Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- CWE-22, Path Traversal: https://cwe.mitre.org/data/definitions/22.html
- CWE-295, Improper Certificate Validation: https://cwe.mitre.org/data/definitions/295.html
