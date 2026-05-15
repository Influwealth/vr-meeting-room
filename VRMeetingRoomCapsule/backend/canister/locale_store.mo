import Trie "mo:base/Trie";
import Principal "mo:base/Principal";

actor LocaleStore {
  public type UserId = Principal;
  public type LangCode = Text;
  public type RoomId = Text;

  stable var userLang : Trie.Trie<UserId, LangCode> = Trie.empty();

  public func setUserLang(user : UserId, lang : LangCode) : async () {
    userLang := Trie.put(userLang, user, lang).0;
  };

  public query func getUserLang(user : UserId) : async ?LangCode {
    Trie.get(userLang, user)
  };

  public query func getRoomLang(roomId : RoomId) : async LangCode {
    let _ = roomId;
    "en"
  };
}

