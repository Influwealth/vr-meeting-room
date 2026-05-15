import Trie "mo:base/Trie";
import Principal "mo:base/Principal";

actor State {
  public type UserId = Principal;
  public type RoomId = Text;
  public type LangCode = Text;

  stable var userLang : Trie.Trie<UserId, LangCode> = Trie.empty();

  public func setUserLang(user : UserId, lang : LangCode) : async () {
    userLang := Trie.put(userLang, user, lang).0;
  };

  public query func getUserLang(user : UserId) : async ?LangCode {
    Trie.get(userLang, user)
  };
}

