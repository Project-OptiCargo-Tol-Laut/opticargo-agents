# Repository initialization policy

- Source, test, script, build, workflow, and package metadata placeholders remain empty pada initial structure.
- README dan docs adalah specification, bukan claim implementation.
- Workflow tetap `.disabled` sampai command nyata lulus lokal.
- Tidak ada wheel/generated artifact/secret yang dibundel.
- Perubahan pertama harus mengisi test dan implementation secara berpasangan sesuai implementation flow.
- Jangan menghapus module/readme/catalog tanpa ADR atau documented structure change.
