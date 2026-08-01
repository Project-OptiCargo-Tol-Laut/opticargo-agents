# Recommendation contract

## Per recommendation

- stable voyage ID;
- recommendation type `backhaul`;
- concise summary;
- ranked cargo combination;
- score breakdown;
- estimated revenue/cost bila input memadai;
- hard constraints checked;
- risks dan alternatives;
- citations;
- confidence;
- fallback flag;
- model mode/version;
- recommended human action.

## Ranked cargo

Menyertakan stable listing/supplier/commodity/port IDs, names, available/selected volume, distance, score, hard constraint status, model metadata, feature explanation, dan warning.

## Invariants

- Selected volume tidak melebihi candidate/voyage capacity.
- Hard constraint invalid tidak muncul.
- Score berada pada range contract.
- Fallback/model metadata konsisten.
- Estimated values memiliki unit/currency eksplisit dan tidak menggunakan floating-point untuk persistence downstream tanpa conversion policy.
- Human action tidak mengklaim transaksi sudah terjadi.

## Persistence

Agents mengembalikan data. Gateway menentukan persistence schema, audit, idempotency, access control, dan lifecycle recommendation.
