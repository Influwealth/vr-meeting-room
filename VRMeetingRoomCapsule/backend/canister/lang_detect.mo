actor LangDetect {
  public type LangCode = Text;

  public query func detectLanguage(text : Text) : async LangCode {
    if (text.size() == 0) { "en" } else { "en" }
  };

  public query func detectFromVoice(audioRef : Text) : async LangCode {
    let _ = audioRef;
    "en"
  };
}

