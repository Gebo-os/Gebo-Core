# Consumer App

See the full guide: [CONSUMER-APP.md](../../CONSUMER-APP.md)

## SDK

```typescript
import { geboClient, loadSession } from "@/lib/geboClient";
const session = await loadSession();
```

## Bootstrap

`GET /integrate/bootstrap` — model, network, capabilities, CLI/integration counts.

## Deploy paths

- **LAN/WiFi:** `.\scripts\start-gebo.ps1`
- **Desktop:** `.\scripts\start-gebo.ps1 -Mode desktop`
- **Docker:** `docker compose up --build`
- **Firebase:** configure `FIREBASE_PROJECT_ID`, use Firebase CLI
