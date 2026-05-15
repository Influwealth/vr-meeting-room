actor TranslationBridge {
  public type LangCode = Text;

  public query func translate(text : Text, from : ?LangCode, to : LangCode) : async Text {
    let _ = from;
    let _ = to;
    text
  };

  public query func generateLocalizedCopy(key : Text, lang : LangCode) : async Text {
    let _ = lang;
    key
  };
}

