# Raman seal ledger — arm 1

**SCORER / SUPPORT-SIDE ⚠️ — not for agent view.**

| Alias | Device (shield) | sha256 of sealed doc | Provenance |
|---|---|---|---|
| vti-01 | JM_R_S_4 | 5b5ffe6ba15784227d6d01ea2f744200b332cab22652297a8854c6888e383434 | `vti-01.wip` (raw Raman, WITec project). Self-hashed by Aaron; email "VTI-01 seal hashes for the campaign ledger", alerts@aaronsharpe.science → zack cc [personal email redacted], 2026-08-19T02:23:27Z, gmail thread [thread id redacted] |
| vti-01 | JM_R_S_4 | d95f4871703f85eb990fe401e1b99f397c8e4e5bb3d960f79f2e9121a520a581 | `vti-01-fused_call.md` (Aaron's precommitted call; contents at unseal). Same email as the `.wip` row |
| vti-02 | — (withheld; files alias-named) | e510beb52ccc4cc93007ef085f5e31070879f4018b4a2028be36a69347c3697e | `vti-02-fused_call.md` (Aaron's precommitted fused Raman + transport call; contents at unseal). Self-hashed by Aaron; email "VTI-02 seal hashes for the campaign ledger", alerts@aaronsharpe.science → zack cc [personal email redacted], 2026-08-22T02:36:16Z, gmail thread 1a027537855afbac |
| vti-02 | — (withheld; files alias-named) | 4b5ed8c7d98bbe99194514f2565488baadef94e0dfb3563a98dec514b8b1175a | `vti-02-raman.md` (Raman document; contents at unseal). Same email as the fused-call row. Aaron's own Raman read — never agent-visible, not an input to the fusion step; at unseal it is compared against HERA's Raman contract as extra credit (Zack ruling, 2026-08-21). Raw Raman map hash to follow as its own row |

Unseal (prereg §5): Aaron commits the tarball itself; its sha256 must match this row.
