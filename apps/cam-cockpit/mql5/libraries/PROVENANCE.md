# libraries/ — DLLs da bridge ZeroMQ (proveniência)

> **SEC-GOV (Kevin):** estas DLLs são carregadas pelo MT5 (`#import` em `cam_zmq.mqh`)
> numa máquina que opera conta **real**. Por isso a proveniência é registrada e
> auditável. A bridge é **read-only** (Art. 35º / CA15.1) — nenhuma DLL aqui envia ordem;
> são apenas o transporte ZeroMQ (sockets PUB/SUB + REQ/REP em 127.0.0.1).

## Origem

Reaproveitadas do pacote **pyzmq 22.3.0** já instalado em
`C:\Python310\Lib\site-packages\pyzmq.libs\` (mesma família de libzmq usada pelo
backend do CaM via `pyzmq>=26`). **Sem download externo, sem build local.**

- `libzmq.dll` — libzmq **4.3.4 x64** (originalmente `libzmq-v142-mt-4_3_4-4e355e3e.dll`,
  renomeada para o nome que o `cam_zmq.mqh` importa).
- `libsodium-138090d4.dll` — dependência de criptografia da libzmq (nome mangled
  preservado: a import table da libzmq referencia esse nome exato).
- `msvcp140.dll`, `vcruntime140.dll`, `vcruntime140_1.dll` — runtime MSVC (deps).

## Hashes SHA-256

```
F8D627EB82530205A48DFBE8C3BE0A34DB663A1D6E2BDBD1E5CB01DB8D694603  libzmq.dll
138090D412AC3537B69C0DF44A24C3C96C8E231BE55F2EE0A7C4638765CAA9D1  libsodium-138090d4.dll
D86AC158123A245B927592C80CC020FEA29C8C4ADDC144466C4625A00CA9C77A  msvcp140.dll
E1D6F78A72836EA120BD27A33AE89CBDC3F3CA7D9D0231AAA3AAC91996D2FA4E  vcruntime140.dll
04E7CCBDCAD7CBAF0ED28692FB08EAB832C38AAD9071749037EE7A58F45E9D7D  vcruntime140_1.dll
```

## Verificação de carga (feita em 2026-06-01)

Carregamento via `ctypes.WinDLL` (simula o loader do MT5) confirmou:
- libzmq **4.3.4**, arquitetura **x64** (compatível com MT5 64-bit);
- todos os 8 exports usados pelo `cam_zmq.mqh` presentes: `zmq_ctx_new`, `zmq_socket`,
  `zmq_bind`, `zmq_send`, `zmq_recv`, `zmq_setsockopt`, `zmq_close`, `zmq_ctx_term`;
- dependências (libsodium + runtime) resolvidas a partir desta mesma pasta.

## Instalação

Copiar **todas** as 5 DLLs desta pasta para o `MQL5\Libraries\` do terminal MT5
(ver `project/runbooks/RUNBOOK-MT5-INSPETOR.md` §1). A `libzmq.dll` precisa das outras
4 ao lado para carregar.
