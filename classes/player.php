<?php
class Player extends DbEntity {
  private $level = 0;
  private $playerPlatoon = 0;
  private $db = NULL;
  private $givenName = NULL;
  private $nickname = NULL;
  private $surname = NULL;
  private $emailaddress = NULL;
  private $password = NULL;
  private $use_nickname = NULL;
  private $platoon_id = NULL;
  private $logintime = NULL;
  private $lastlogintime = NULL;
  private $gm = NULL;
  private $gmRpgId = NULL;
  private $gmActive = NULL;
  private $admin = NULL;

  function __construct($playerId = NULL) {
    $this->level = $_SESSION ['level'];
    if (array_key_exists('platoon_id', $_SESSION)) {
      $this->playerPlatoon = $_SESSION ['platoon_id'];
    }
    $this->db = getDatabaseConnection();
    if ($playerId == NULL) {
      if (array_key_exists('user_id', $_SESSION)) {
        $this->id = $_SESSION ['user_id'];
      }
    } else {
      $this->id = $playerId;
    }
  }

  //TODO remove this functionality
  public function loadData() {
    if ($this->id == NULL) {
      return;
    }
    $playersql = "SELECT forname, nickname, lastname, emailadress, use_nickname, platoon_id,
        logintime, lastlogintime, GMs.userid as gm, GMs.RPG_id, GMs.active, ".
        "Admins.userid as admin, count(*) as howmany FROM Users " .
        "LEFT JOIN GMs on GMs.userid = Users.id " .
        "LEFT JOIN Admins on Admins.userid = Users.id WHERE Uers.id = :userid";
    $stmt = $this->db->prepare($playersql);
    $stmt->bindValue(':userid', $this->id, PDO::PARAM_INT);
    $stmt->execute();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    if ($row ['howmany'] == 1) {
      $this->givenName = $row ['forname'];
      $this->nickname = $row ['nickname'];
      $this->surname = $row ['lastname'];
      $this->emailaddress = $row ['emailadress'];
      $this->use_nickname = $row ['use_nickname'];
      $this->platoon_id = $row ['platoon_id'];
      $this->logintime = $row ['logintime'];
      $this->lastlogintime = $row ['lastlogintime'];
      if ($row['gm']) {
        $this->gm = TRUE;
      } else {
        $this->gm = FALSE;
      }
      $this->gmRpgId = $row['RPG_id'];
      $this->gmActive = $row['active'];
      if ($row['admin']) {
        $this->admin = TRUE;
      } else {
        $this->admin = FALSE;
      }
    }
  }

  public function getId() {
    return $this->id;
  }

  public function setId($id) {
    $this->id = $id;
  }

  public function getName() {
    return $this->givenName . ' ' . $this->surname;
  }

  public function getNameWithNickname() {
    $name = $this->givenName;
    if ($this->use_nickname) {
      $name .= " '" . $this->nickname . "'";
    }
    $name .= " " . $this->surname;
    return $name;
  }

    public function getGivenName() {
    return $this->givenName;
  }

  public function setGivenName($name) {
    $this->givenName = $name;
  }

  public function getSurname() {
    return $this->surname;
  }

  public function setSurname($name) {
    $this->surname = $name;
  }

  public function getUseNickname() {
    return $this->use_nickname;
  }

  public function setUseNickname($use) {
    $this->use_nickname = $use;
  }

  public function getNickname() {
    return $this->nickname;
  }

  public function setNickname($name) {
    $this->nickname = $name;
  }

  public function getEmailaddress() {
    return $this->emailaddress;
  }

  public function setEmailaddress($email) {
    $this->emailaddress = $email;
  }

  public function getPassword() {
    return $this->password;
  }

  public function setPassword($password) {
    $this->password = $password;
  }

  public function getPlatoonId() {
    return $this->platoon_id;
  }

  public function setPlatoonId($id) {
    $this->platoon_id = $id;
  }

  public function getLoginTime() {
    return $this->logintime;
  }

  public function setLoginTime($time) {
    $this->logintime = $time;
  }

  public function getLastLoginTime() {
    return $this->lastlogintime;
  }

  public function setLastLoginTime($time) {
    $this->lastlogintime = $time;
  }

  public function getGmRpgId() {
    return $this->gmRpgId;
  }

  public function setGmRpgId($rpgId) {
    $this->gmRpgId = $rpgId;
  }

  public function getGmActive() {
    return $this->gmActive;
  }

  public function setGmActive($active) {
    $this->gmActive = $active;
  }

  public function isAdmin() {
    if ($this->admin != NULL) {
      return $this->admin;
    } else {
      return ($this->level == 3) ? (TRUE) : (FALSE);
    }
  }

  public function setAdmin($value) {
    $this->admin = $value;
  }

  public function isGm() {
  if ($this->gm != NULL) {
      return $this->gm;
    } else {
      return ($this->level == 2) ? (TRUE) : (FALSE);
    }
  }

  public function setGm($value) {
    $this->gm = $value;
  }
}
