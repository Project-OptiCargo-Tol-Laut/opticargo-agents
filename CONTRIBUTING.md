# Contributing

Setiap perubahan harus memiliki scope terbatas, requirement/acceptance, file in-scope, contract version, test plan, failure behavior, observability impact, dan evidence.

## Minimum change quality

- Tidak mendefinisikan ulang contract `opticargo-shared` tanpa versioning dan compatibility test.
- Tidak mengimpor sibling repository melalui source path.
- Tidak menambahkan mutation booking, payment, user, atau transaksi ke Agents.
- Hard constraint dan evidence validation tetap berada di luar kendali LLM.
- Perubahan endpoint atau SSE event memiliki contract test dan compatibility note.
- Test relevan ditambahkan pada layer yang benar.
- Secret, API key, token, PII nyata, full evidence document, dan raw provider response tidak masuk repository, log, metric label, atau fixture.
- README folder, catalog, traceability, dan ADR diperbarui bila keputusan berubah.

Gunakan template issue dan pull request pada `.github/`.
