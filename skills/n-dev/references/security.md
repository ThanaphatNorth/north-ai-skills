# Security: the boundary, access and exposure

> Read when: the change takes anything from outside the process, changes who may see or do what, returns or logs
> stored data, calls another service, or adds a dependency (steps 3 and 6 of SKILL.md).
"Outside" means: a file or archive someone else made, a network response, an environment variable, a CLI argument,
a request body, a path or name a user typed, a queue message, another machine's output.

Every row is a question to answer with a line of code or a test, not with an opinion. A "yes, and here is the line"
goes in the report; a "no" is a finding.

| Area | Ask | Typical failure | Check |
|---|---|---|---|
| **Archives and paths** | Is every entry name / joined path proven to stay inside the target folder, before anything is written? | `tar -xf` after looking only at the first entry; `path.join(base, userInput)` with `../` | A test that unpacks an archive with a `../` or absolute entry in the middle and sees it refused |
| **Verify, then use** | Does signature / checksum verification happen **before** unpack, execute or install, on the exact bytes used? | Unpacking first and verifying later; verifying one file and running another | A test where the signature is wrong and nothing was written or run |
| **Remote code** | Is anything fetched and then executed (`curl … \| bash`, `eval`, dynamic `require`)? If yes, is the source pinned (key pin, digest) and is `-k`/`--insecure` absent? | A "trusted URL" with TLS checks off | grep the change for `\| *(ba)?sh`, `-k `, `--insecure`, `rejectUnauthorized: *false`; each hit needs a pin or a stated reason (a loopback health check is a valid reason) |
| **Shell and process** | Does any user-controlled string reach a shell? | `exec(\`cmd ${x}\`)`, `sh -c`, `shell: true` | Argument arrays only (`execFile`, `spawn` without a shell); a test with `; touch x` in the input |
| **State files** | Is every state file written atomically (temp file in the same folder, then rename), and what does a failed read return? | `writeFile` interrupted → invalid JSON → reader falls back to "empty" → replay protection or locks silently off | A test that corrupts the file and sees a loud failure, not an empty default |
| **Secrets** | Who can read the file, the env var, the log line? Does a token reach a child process or a build step that does not need it? | World-readable env files; a login token exported to every build | File mode asserted in a test (0600 / 0640); the child's env built from an allow-list |
| **Auth and sessions** | Does every state-changing route check identity, role and a CSRF guard? Is a plain-HTTP start refused or loud? | A route added without the guard; the cookie loses `Secure` over HTTP | One test per new route: no session → 401, wrong role → 403 |
| **Access to each record** | Does every read and write by id check that this caller may see or change **that** record, and are list queries scoped to the caller? | `GET /orders/:id` checks the login but not the owner (IDOR); a list filtered only in the UI | One test per new route or query: another user's id → 403 or 404, and the list holds only the caller's rows |
| **Injection** | Does any input reach a query, template, header or expression as code rather than as a bound value? | SQL or NoSQL built by string concatenation; a raw query with `${x}`; user text in a template that is compiled | Bound parameters or the query builder only; a test with `' OR '1'='1` (or `{"$ne": null}`) in the input |
| **Output encoding** | Is every value rendered into HTML, a URL or a script escaped for that place? | `innerHTML`, `dangerouslySetInnerHTML`, `v-html` with user text | Escaping by the framework, or a sanitizer named in code; a test with `<img src=x onerror=…>` that renders as text |
| **Data exposure** | Do responses, errors and logs carry only what the caller needs, with no secret, token or personal data beyond that? | a whole user row (password hash, tokens) in a response; a stack trace or SQL in an error; an ID card number in a log line | A test that the response holds only the named fields; grep the diff's log lines for tokens and personal fields |
| **Outbound requests and redirects** | Can input choose the host or path of a request the server makes, or of a redirect it sends? | fetching a URL a user typed (SSRF), reaching internal addresses or cloud metadata; `?next=` sending users to another site | An allow-list of hosts or relative paths only; a test with `http://169.254.169.254/`, `http://localhost/` and `//evil.example` refused |
| **Dependencies** | Is each new package needed, maintained, pinned in the lockfile and clean in the repo's audit? | a package added for one helper; an install script; a known advisory at high | The lockfile in the diff; the repo's audit output (run by QA in a loop) clean at high; no audit command → say so in the report |
| **Mass assignment** | Does a write take only the fields the caller may set, from an allow-list? | `update({ data: req.body })` lets a caller set `role`, `ownerId` or `price` | A schema or DTO that lists the writable fields; a test that sends `role` and sees it ignored or refused |
| **Secrets in the client** | Does any secret reach code shipped to a browser or a phone? | an API key in a `NEXT_PUBLIC_`, `VITE_` or `EXPO_PUBLIC_` variable; a service key in the app bundle | grep the diff for public-prefixed env names and keys; secrets stay behind the server |
| **Tokens on the device** | Are tokens and personal data on a phone kept in the platform's secure store? | a session token in AsyncStorage or SharedPreferences | Keychain / Keystore (or the framework's secure-store wrapper) in code |
| **Deploy and CI config** | Does a change to CI, containers or infrastructure widen who can reach or run what? | a workflow on `pull_request_target` that checks out the PR's code; `permissions: write-all`; a container running as root; CORS `*` with credentials; a public bucket or port | The config line, at least privilege; a stated reason for each widening |
| **Randomness and comparison** | Are tokens, codes and ids that must be unguessable made by a crypto random source, and secrets compared in constant time? | `Math.random()` for a reset code; `==` on a signature | `crypto.randomBytes` / `secrets` / the platform's equivalent in code; a constant-time compare |
| **Abuse limits** | Are login, OTP, reset, search and other costly or guessable endpoints rate-limited, keyed on something the attacker cannot vary for free? | unlimited OTP tries; a limit keyed only on the e-mail an attacker types | A test that the next attempt after the limit is refused |
| **Concurrency and replay** | Can the same command run twice, or two writers interleave? | Dead connections kept in a waiter list; nonce store lost on crash | A test for the second delivery and for a closed connection |
| **Input size and time** | Is every body, upload and loop bounded, with a timeout? | Unbounded read into memory; no request timeout | A test with an oversized input |

## When it applies

- **Tiny** change: only the rows the change touches.
- **Standard / Large**: walk the whole table once in step 3 for the boundaries the design note lists, and again over the diff in step 6.
- A change that touches none of these says so in one line in the report ("no security-relevant path").

## Rules

- A finding in code you did not touch is reported, not fixed, unless the task asks (same rule as existing debt).
- A fix starts with a test that reproduces the attack input and is seen red for that reason.
- Never put a real secret in a test; use a generated value.

## Sources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP, Path Traversal: https://owasp.org/www-community/attacks/Path_Traversal
- OWASP, Cross-Site Request Forgery Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP, OS Command Injection Defense Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- OWASP, Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP, SQL Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
- OWASP, Cross Site Scripting Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- OWASP, Server Side Request Forgery Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html
- OWASP, Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- OWASP, Vulnerable Dependency Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html
- CWE-22, Path Traversal: https://cwe.mitre.org/data/definitions/22.html
- CWE-639, Authorization Bypass Through User-Controlled Key: https://cwe.mitre.org/data/definitions/639.html
- CWE-295, Improper Certificate Validation: https://cwe.mitre.org/data/definitions/295.html
