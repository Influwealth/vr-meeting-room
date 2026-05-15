# VR Meeting Room — Sovereign OS / WealthBridge OS Capsule
### Immersive VR Pitch Room • Product Walkthrough Hall • Multi-Language Africa Engine • ICP-Powered Backend

The **VR Meeting Room Capsule** is a sovereign, Oculus-ready, WebXR-enabled virtual environment designed for business meetings, pitch decks, product walkthroughs, and interactive simulations.
It integrates directly with **WealthBridge OS**, **Sovereign OS**, and **ICP canisters**, enabling real-time data, agent interactions, and multi-language support for 2,000+ African languages.

## Features

### 1. Immersive VR Meeting Room
- Holographic table
- Multi-user avatars + spatial audio
- Live pitch deck viewer (PDF, Slides, Video)
- Multi-window browser support
- Presenter mode + laser pointer

### 2. Product Walkthrough Hall
Each WealthBridge capsule appears as an interactive 3D pod:
- Business Registry Capsule
- Unit Capsule (BRICS trade currency)
- Rewards Capsule
- Tradeline Capsule
- Metabolic Modeling Capsule
- Smart City Capsule
- Quantum Internet / NVQLink Pod
- Dames Legacy Accounts Pod
- And more...

Each pod supports:
- Live data from WealthBridge OS
- Run Simulation
- Show Audit Trail
- Deploy Capsule

### 3. Sandbox Simulation Room
- Economic simulations
- Metabolic networks
- Smart city models
- Quantum flows
- Agent orchestration demos

### 4. African Multi-Language Engine (2,000+ languages)

Components:
- `lang_detect.mo` - language detection (text + voice)
- `locale_store.mo` - per-user + per-room language preferences
- `translation_bridge.mo` - sovereign translation + generation bridge
- `lang_agent.py` - presenter + QAssist language routing
- `languages.json` - language families + fallback chains

UX:
- Auto-detect user language from voice
- UI + subtitles localized
- Host can set room language
- Users can override individually

## Architecture

```text
/VRMeetingRoomCapsule
  /frontend
    /unity
      Scenes/
        MeetingRoom.unity
        ProductHall.unity
        Sandbox.unity
      Scripts/
        VRRoomManager.cs
        ProductPodController.cs
        PitchDeckController.cs
        AvatarManager.cs
        LangRouterClient.cs
        VoiceCommandClient.cs
    /webxr
      src/
        index.tsx
        LangRouterClient.ts
  /backend
    /canister
      main.mo
      api.mo
      auth.mo
      state.mo
      lang_detect.mo
      locale_store.mo
      translation_bridge.mo
    /integrations
      wealthbridge_api.mo
      qassist_api.mo
      meshvault_api.mo
      observability_api.mo
  /agents
    presenter_agent.py
    simulation_agent.py
    catalog_agent.py
    lang_agent.py
  /config
    capsule.json
    permissions.json
    routes.json
    languages.json
```

## Deployment (Scaffold)

This repository is scaffold-only and dependency-free by design.

Typical deployment pipeline (to be implemented in later phases):
1. Build Unity client (Oculus/WebXR)
2. Upload assets to MeshVault
3. Deploy canisters (`dfx deploy`)
4. Register capsule in WealthBridge OS
5. Enable Observability + QAssist

## License

TBD.
