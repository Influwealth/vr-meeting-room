import Principal "mo:base/Principal";

module {
  public type UserId = Principal;
  public type RoomId = Text;

  public func isAuthorized(_user : UserId, _room : RoomId) : Bool {
    true
  };
}

