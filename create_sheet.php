<?php
/*
 * Note: libPDF uses coordinates from the lower left corner
 */
session_start ();
include "functions.php";
include "iconpdf.php";

$characterId = $_GET['character_id'];
$character = new Character($characterId);
$user = new Player();

$userid = $character->getPlayer();

if ($user->getPlayerId() == $character->getPlayer() || $user->isAdmin() || $user->isGm()) {
  $platoon_id = $character->getPlatoon();
  $player = new Player($character->getPlayer());
  $player->loadData();
  $character->loadData();
  $bonuses = new Bonus($characterId);

  function fontregular($font, $pdf) {
    $font = PDF_load_font ( $pdf, "Helvetica", "host", 0 );
    pdf_setfont ( $pdf, $font, 10 );
  }

  function fontbold($font, $pdf) {
    $font = PDF_load_font ( $pdf, "Helvetica-Bold", "host", 0 );
    pdf_setfont ( $pdf, $font, 10 );
  }

  $aapcolumnone = 50;
  $aapcolumntwo = 110;
  $aapcolumnthree = 120;
  $attribpcolumnthree = 160;
  $aapcolumnfour = 200; // 170
  $aapcolumnfive = 290; // 260
  $aapcolumnsix = 310; // 280

  $pdf = pdf_new ();

  pdf_open_file ( $pdf, "" );
  pdf_set_parameter ( $pdf, "warning", "true" );

  pdf_set_info ( $pdf, "Creator", "create_sheet.php" );
  pdf_set_info ( $pdf, "Author", "Skynet" );
  pdf_set_info ( $pdf, "Title", "Character Sheet, USCM" );

  pdf_begin_page ( $pdf, 595, 842 );
  $font = PDF_load_font ( $pdf, "Helvetica", "host", 0 );
  pdf_setfont ( $pdf, $font, 10 );

  PDF_image ( $pdf, "./resources/logoimage_sized.png", 50, 700, 280, 102 );

  pdf_set_text_pos ( $pdf, 50, 690 );
  pdf_show ( $pdf, "Character sheet" );
  pdf_set_text_pos ( $pdf, 290, 690 );
  pdf_show ( $pdf, "www.uscm.tk" );

//   $character = characterdata($characterId);
  pdf_set_text_pos ( $pdf, 50, 670 );
  pdf_show ( $pdf, "Player" );
  pdf_set_text_pos ( $pdf, 100, 670 );
  pdf_show ( $pdf, $player->getGivenName() . " " . $player->getSurname());

  pdf_set_text_pos ( $pdf, 50, 656 );
  pdf_show ( $pdf, "Email" );
  pdf_set_text_pos ( $pdf, 100, 656 );
  pdf_show ( $pdf, $player->getEmailaddress());

  pdf_set_text_pos ( $pdf, 50, 627 );
  pdf_show ( $pdf, "Name" );
  pdf_set_text_pos ( $pdf, 100, 627 );
  pdf_show ( $pdf, $character->getName());

  pdf_set_text_pos ( $pdf, 50, 615 );
  pdf_show ( $pdf, "Rank" );
  pdf_set_text_pos ( $pdf, 100, 615 );
  pdf_show ( $pdf, $character->getRankLong());

  pdf_set_text_pos ( $pdf, 50, 603 );
  pdf_show ( $pdf, "Specialty" );
  pdf_set_text_pos ( $pdf, 100, 603 );
  pdf_show ( $pdf, $character->getSpecialtyName());

  pdf_set_text_pos ( $pdf, 50, 591 );
  pdf_show ( $pdf, "Enlisted" );
  pdf_set_text_pos ( $pdf, 100, 591 );
  pdf_show ( $pdf, $character->getEnlistedDate());

  pdf_set_text_pos ( $pdf, 50, 579 );
  pdf_show ( $pdf, "Age" );
  pdf_set_text_pos ( $pdf, 100, 579 );
  pdf_show ( $pdf, $character->getAge());

  pdf_set_text_pos ( $pdf, 50, 567 );
  pdf_show ( $pdf, "Gender" );
  pdf_set_text_pos ( $pdf, 100, 567 );
  pdf_show ( $pdf, $character->getGender());

  // Attributes
  fontbold ( $font, $pdf );
  pdf_set_text_pos ( $pdf, $aapcolumnone, 534 );
  pdf_show ( $pdf, "Attributes" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 534 );
  pdf_show ( $pdf, "Level" );
  pdf_set_text_pos ( $pdf, $attribpcolumnthree, 534 );
  pdf_show ( $pdf, "Bonus" );

  fontregular ( $font, $pdf );
  $attributearray = characterattributes($characterId);
  $height = 520;
  foreach ($attributearray as $attributeid => $attribute) {
    pdf_set_text_pos ( $pdf, $aapcolumnone, $height );
    pdf_show ( $pdf, $attribute ['attribute_name'] );

    pdf_set_text_pos ( $pdf, $aapcolumntwo, $height );
    pdf_show ( $pdf, $attribute ['value'] );
    $attributepointsbonus = $bonuses->attributeBonus("modifier_basic_value", $attributeid);
    pdf_set_text_pos ( $pdf, $aapcolumntwo + 10, $height );
    print_pdf_bonus ( $pdf, $attributepointsbonus );

    pdf_set_text_pos ( $pdf, $attribpcolumnthree, $height );
    $attributepointsbonus = $bonuses->attributeBonus("modifier_dice_value", $attributeid);
    print_pdf_bonus ( $pdf, $attributepointsbonus );
    $height -= 12;
  }

  // Points
  fontbold ( $font, $pdf );
  pdf_set_text_pos ( $pdf, $aapcolumnone, 388 );
  pdf_show ( $pdf, "Points" );

  fontregular ( $font, $pdf );
  pdf_set_text_pos ( $pdf, $aapcolumnone, 374 );
  pdf_show ( $pdf, "Experience:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 374 );
  pdf_show ( $pdf, $character->getUnusedXp());

  pdf_set_text_pos ( $pdf, $aapcolumnone, 362 );
  pdf_show ( $pdf, "Cool Points:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 362 );
  pdf_show ( $pdf, $character->getCoolPoints());

  pdf_set_text_pos ( $pdf, $aapcolumnone, 350 );
  pdf_show ( $pdf, "Awareness:" );

  // pdf_setlinewidth($pdf,.5);
  $awareness = $character->getAwareness();
  $awarenessbonus = $bonuses->pointAndLimitBonus("awareness");
  if ($awarenessbonus ['always'] != 0) {
    $awareness += $awarenessbonus ['always'];
  }
  $awarenessbonussometimes = 0;
  if (is_array ( $awarenessbonus ['sometimes'] )) {
    foreach ( $awarenessbonus ['sometimes'] as $bonus ) {
      $awarenessbonussometimes += $bonus;
    }
  }
  $width = 8;
  $height = 8;
  $xpos = $aapcolumntwo;
  if ($awarenessbonussometimes >= 0) {
    $white = $awareness;
    $lightgrey = $awareness + $awarenessbonussometimes;
  } else {
    // use addition since $awarenessbonussometimes is negative
    $white = $awareness + $awarenessbonussometimes;
    $lightgrey = $awareness;
  }
  /*
   * print_r($white);
   * print_r($lightgrey);
   * print_r($awareness);
   * print_r($awarenessbonus);
   */
  pdf_setcolor ( $pdf, "fill", "gray", 0.8, 0, 0, 0 );
  for($i = 1; $i <= 10; $i ++) {
    if ($i > $lightgrey) {
      pdf_setcolor ( $pdf, "fill", "gray", 0.4, 0, 0, 0 );
    }
    pdf_rect ( $pdf, $xpos, 350, $width, $height );
    if ($i <= $white) {
      pdf_stroke ( $pdf );
    } else {
      // pdf_fill_stroke($pdf);
      $pdf->Rect ( $xpos, 484, $width, $height, 'DF', array (
          'all' => array (
              'width' => 1,
              'cap' => 'round',
              'join' => 'round',
              'color' => array (
                  0,
                  0,
                  0
              )
          )
      ), array (
          190,
          190,
          190
      ) );
    }
    $xpos += $width;
  }

  pdf_setcolor ( $pdf, "fill", "gray", 0, 0, 0, 0 );

  pdf_set_text_pos ( $pdf, $aapcolumnone, 338 );
  pdf_show ( $pdf, "Leadership:" );
  $leadership = $character->getLeadership();
  $leadershipbonus = $bonuses->pointAndLimitBonus("leadership");
  if ($leadershipbonus ['always'] != 0) {
    $leadership += $leadershipbonus ['always'];
  }
  $leadershipbonussometimes = 0;
  if (is_array($leadershipbonus ['sometimes'])) {
    foreach ($leadershipbonus ['sometimes'] as $bonus) {
      $leadershipbonussometimes += $bonus;
    }
  }
  $width = 8;
  $height = 8;
  $xpos = $aapcolumntwo;
  pdf_setcolor ( $pdf, "fill", "gray", 0.9, 0, 0, 0 );
  if ($leadershipbonussometimes >= 0) {
    $white = $leadership;
    $lightgrey = $leadership + $leadershipbonussometimes;
  } else {
    // use addition since $leadershipbonussometimes is negative
    $white = $leadership + $leadershipbonussometimes;
    $lightgrey = $leadership;
  }
  for ($i = 1; $i <= 10; $i ++) {
    if ($i <= $white) {
      $pdf->Rect ( $xpos, 496, $width, $height, 'DF', array (
          'all' => array (
              'width' => 1,
              'cap' => 'round',
              'join' => 'round',
              'color' => array (
                  0,
                  0,
                  0
              )
          )
      ), array (
          255,
          255,
          255
      ) );
    } else {
      $pdf->Rect ( $xpos, 496, $width, $height, 'DF', array (
          'all' => array (
              'width' => 1,
              'cap' => 'round',
              'join' => 'round',
              'color' => array (
                  0,
                  0,
                  0
              )
          )
      ), array (
          190,
          190,
          190
      ) );
    }
    $xpos += $width;
  }
  pdf_setcolor ( $pdf, "fill", "gray", 0, 0, 0, 0 );
  pdf_set_text_pos ( $pdf, $aapcolumnone, 326 );

  pdf_show ( $pdf, "Psycho:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 326 );
  pdf_show ( $pdf, $character->getPsychoPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnthree, 326 );
  $psychopointsbonus = $bonuses->psychoPoints();
  print_pdf_bonus ( $pdf, $psychopointsbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnone, 314 );
  pdf_show ( $pdf, "Fear:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 314 );
  pdf_show ( $pdf, $character->getFearPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnthree, 314 );
  $fearpointsbonus = $bonuses->fearPoints();
  print_pdf_bonus ( $pdf, $fearpointsbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnone, 302 );
  pdf_show ( $pdf, "Exhaustion:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 302 );
  pdf_show ( $pdf, $character->getExhaustionPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnthree, 302 );
  $exhaustionpointsbonus = $bonuses->exhaustionPoints();
  print_pdf_bonus ( $pdf, $exhaustionpointsbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnone, 290 );
  pdf_show ( $pdf, "Trauma:" );
  pdf_set_text_pos ( $pdf, $aapcolumntwo, 290 );
  pdf_show ( $pdf, $character->getTraumaPoints());

  pdf_set_text_pos ( $pdf, $aapcolumnfour, 374 );
  pdf_show ( $pdf, "Carry Capacity:" );
  pdf_set_text_pos ( $pdf, $aapcolumnfive, 374 );
  pdf_show ( $pdf, $character->getCarryCapacity());
  pdf_set_text_pos ( $pdf, $aapcolumnsix, 374 );
  $carrybonus = $bonuses->carryCapacity();
  print_pdf_bonus ( $pdf, $carrybonus );

  pdf_set_text_pos ( $pdf, $aapcolumnfour, 362 );
  pdf_show ( $pdf, "Combat Load:" );
  pdf_set_text_pos ( $pdf, $aapcolumnfive, 362 );
  pdf_show ( $pdf, $character->getCombatLoad());
  pdf_set_text_pos ( $pdf, $aapcolumnsix, 362 );
  $combatbonus = $bonuses->combatLoad();
  print_pdf_bonus ( $pdf, $combatbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnfour, 326 );
  pdf_show ( $pdf, "Psycho Limit:" );
  pdf_set_text_pos ( $pdf, $aapcolumnfive, 326 );
  pdf_show ( $pdf, $character->getPsychoPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnsix, 326 );
  $psycholimitbonus = $bonuses->psychoLimit();
  print_pdf_bonus ( $pdf, $psycholimitbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnfour, 314 );
  pdf_show ( $pdf, "Fear Limit:" );
  pdf_set_text_pos ( $pdf, $aapcolumnfive, 314 );
  pdf_show ( $pdf, $character->getFearPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnsix, 314 );
  $fearlimitbonus = $bonuses->fearLimit();
  print_pdf_bonus ( $pdf, $fearlimitbonus );

  pdf_set_text_pos ( $pdf, $aapcolumnfour, 302 );
  pdf_show ( $pdf, "Exhaustion Limit:" );
  pdf_set_text_pos ( $pdf, $aapcolumnfive, 302 );
  pdf_show ( $pdf, $character->getExhaustionPoints());
  pdf_set_text_pos ( $pdf, $aapcolumnsix, 302 );
  $exhaustionlimitbonus = $bonuses->exhaustionLimit();
  print_pdf_bonus ( $pdf, $exhaustionlimitbonus );

  // Missions
  fontbold ( $font, $pdf );
  $missionheight = 260;
  pdf_set_text_pos ( $pdf, 50, $missionheight );
  pdf_show ( $pdf, "Missions" );
  fontregular ( $font, $pdf );
  $missionarray = $character->getMissionsShort();
  $missionheight -= 12;
  foreach ( $missionarray as $mission ) {
    pdf_set_text_pos ( $pdf, 50, $missionheight );
    pdf_show ( $pdf, $mission ['mission_name'] );
    pdf_set_text_pos ( $pdf, 90, $missionheight );
    pdf_show ( $pdf, $mission ['text'] );
    $missionheight -= 12;
  }

  // Medals
  fontbold ( $font, $pdf );
  $commendationheight = 494;
  pdf_set_text_pos ( $pdf, 220, 494 );
  pdf_show ( $pdf, "Commendations" );
  fontregular ( $font, $pdf );
  $medalarray = $character->getMedals();
  $commendationheight -= 12;
  foreach ( $medalarray as $medal ) {
    pdf_set_text_pos ( $pdf, 220, $commendationheight );
    pdf_show ( $pdf, $medal ['medal'] );
    $commendationheight -= 12;
  }

  // Certificates
  fontbold ( $font, $pdf );
  $certificateheight = 639;
  pdf_set_text_pos ( $pdf, 220, $certificateheight );
  pdf_show ( $pdf, "Certificates" );
  fontregular ( $font, $pdf );
  $certificatearray = $character->getCertificates();
  $certificateheight -= 12;
  foreach ( $certificatearray as $certificate ) {
    pdf_set_text_pos ( $pdf, 220, $certificateheight );
    pdf_show ( $pdf, $certificate ['name'] );
    $certificateheight -= 12;
  }

  // Traits
  fontbold ( $font, $pdf );
  $traitsheight = 260;
  pdf_set_text_pos ( $pdf, 170, $traitsheight );
  pdf_show ( $pdf, "Traits" );
  fontregular ( $font, $pdf );
  $traitarray = traits($characterId);
  $traitsheight -= 12;
  foreach ( $traitarray as $trait ) {
    pdf_set_text_pos ( $pdf, 170, $traitsheight );
    pdf_show ( $pdf, $trait ['trait_name'] );
    $traitsheight -= 12;
  }

  // Advantages
  fontbold ( $font, $pdf );
  $advheight = 200;
  if ($traitsheight - 12 < $advheight) {
    $advheight = $traitsheight - 12;
  }

  pdf_set_text_pos ( $pdf, 170, $advheight );
  pdf_show ( $pdf, "Advantages" );
  fontregular ( $font, $pdf );
  $advarray = $character->getAdvantages();
  $advheight -= 12;
  foreach ( $advarray as $adv ) {
    pdf_set_text_pos ( $pdf, 170, $advheight );
    pdf_show ( $pdf, $adv ['advantage_name'] );
    $advheight -= 12;
  }

  // Disadvantages
  fontbold ( $font, $pdf );
  $disadvheight = 260;
  pdf_set_text_pos ( $pdf, 280, $disadvheight );
  pdf_show ( $pdf, "Disadvantages" );
  fontregular ( $font, $pdf );
  $disadvarray = $character->getDisadvantages();
  $disadvheight -= 12;
  foreach ( $disadvarray as $disadv ) {
    pdf_set_text_pos ( $pdf, 280, $disadvheight );
    pdf_show ( $pdf, $disadv ['disadvantage_name'] );
    $disadvheight -= 12;
  }

  // Skills
  fontbold ( $font, $pdf );
  $skillsheight = 710;
  pdf_set_text_pos ( $pdf, 380, $skillsheight );
  pdf_show ( $pdf, "Skills" );
  pdf_set_text_pos ( $pdf, 470, $skillsheight );
  pdf_show ( $pdf, "Level" );
  pdf_set_text_pos ( $pdf, 500, $skillsheight );
  pdf_show ( $pdf, "Bonus" );
  fontregular ( $font, $pdf );
  $skillarray = $character->getWeaponSkills();
  $skillsheight -= 12;
  foreach ( $skillarray as $skill ) {
    pdf_set_text_pos ( $pdf, 380, $skillsheight );
    pdf_show ( $pdf, $skill ['name'] );

    pdf_set_text_pos ( $pdf, 480, $skillsheight );
    pdf_show ( $pdf, $skill ['value'] );
    pdf_set_text_pos ( $pdf, 500, $skillsheight );
    if ($skill ['bonus_always'] != 0) {
      if ($skill ['bonus_always'] > 0) {
        $bonussign = "+";
      } else {
        $bonussign = "-";
      }
      pdf_show ( $pdf, $bonussign . $skill ['bonus_always'] . " " );
    }
    if (is_array ( $skill ['bonus_sometimes'] )) {
      foreach ( $skill ['bonus_sometimes'] as $bonus ) {
        if ($bonus > 0) {
          $bonussign = "+";
        } else {
          $bonussign = "-";
        }
        pdf_show ( $pdf, " (" . $bonussign . $bonus . ") " );
      }
    }
    $skillsheight -= 12;
  }
  $skillsheight -= 12;
  $skillarray = $character->getPhysicalSkills();
  foreach ( $skillarray as $skill ) {
    pdf_set_text_pos ( $pdf, 380, $skillsheight );
    pdf_show ( $pdf, $skill ['name'] );

    pdf_set_text_pos ( $pdf, 480, $skillsheight );
    pdf_show ( $pdf, $skill ['value'] );

    pdf_set_text_pos ( $pdf, 500, $skillsheight );
    if ($skill ['bonus_always'] != 0) {
      if ($skill ['bonus_always'] > 0) {
        $bonussign = "+";
      } else {
        $bonussign = "-";
      }
      pdf_show ( $pdf, $bonussign . $skill ['bonus_always'] );
    }
    if (is_array ( $skill ['bonus_sometimes'] )) {
      foreach ( $skill ['bonus_sometimes'] as $bonus ) {
        if ($bonus > 0) {
          $bonussign = "+";
        } else {
          $bonussign = "-";
        }
        pdf_show ( $pdf, " (" . $bonussign . $bonus . ") " );
      }
    }
    $skillsheight -= 12;
  }

  $skillsheight -= 12;
  $skillarray = $character->getVehiclesSkills();
  foreach ( $skillarray as $skill ) {
    pdf_set_text_pos ( $pdf, 380, $skillsheight );
    pdf_show ( $pdf, $skill ['name'] );

    pdf_set_text_pos ( $pdf, 480, $skillsheight );
    pdf_show ( $pdf, $skill ['value'] );

    pdf_set_text_pos ( $pdf, 500, $skillsheight );
    if ($skill ['bonus_always'] != 0) {
      if ($skill ['bonus_always'] > 0) {
        $bonussign = "+";
      } else {
        $bonussign = "-";
      }
      pdf_show ( $pdf, $bonussign . $skill ['bonus_always'] );
    }
    if (is_array ( $skill ['bonus_sometimes'] )) {
      foreach ( $skill ['bonus_sometimes'] as $bonus ) {
        if ($bonus > 0) {
          $bonussign = "+";
        } else {
          $bonussign = "-";
        }
        pdf_show ( $pdf, " (" . $bonussign . $bonus . ") " );
      }
    }
    $skillsheight -= 12;
  }
  $skillsheight -= 12;
  $skillarray = $character->getOtherSkills();
  foreach ( $skillarray as $skill ) {
    pdf_set_text_pos ( $pdf, 380, $skillsheight );
    pdf_show ( $pdf, $skill ['name'] );

    pdf_set_text_pos ( $pdf, 480, $skillsheight );
    pdf_show ( $pdf, $skill ['value'] );

    pdf_set_text_pos ( $pdf, 500, $skillsheight );
    if ($skill ['bonus_always'] != 0) {
      if ($skill ['bonus_always'] > 0) {
        $bonussign = "+";
      } else {
        $bonussign = "-";
      }
      pdf_show ( $pdf, $bonussign . $skill ['bonus_always'] );
    }
    if (is_array ( $skill ['bonus_sometimes'] )) {
      foreach ( $skill ['bonus_sometimes'] as $bonus ) {
        if ($bonus > 0) {
          $bonussign = "+";
        } else {
          $bonussign = "-";
        }
        pdf_show ( $pdf, " (" . $bonussign . $bonus . ") " );
      }
    }
    $skillsheight -= 12;
  }
  $skillsheight -= 12;
  $skillarray = $character->getLanguagesSkills();
  foreach ( $skillarray as $skill ) {
    pdf_set_text_pos ( $pdf, 380, $skillsheight );
    pdf_show ( $pdf, $skill ['name'] );

    pdf_set_text_pos ( $pdf, 480, $skillsheight );
    pdf_show ( $pdf, $skill ['value'] );

    pdf_set_text_pos ( $pdf, 500, $skillsheight );
    // pdf_show($pdf,$skill['bonus']);
    $skillsheight -= 12;
  }

  pdf_end_page ( $pdf );
  pdf_close ( $pdf );

  $buf = pdf_get_buffer ( $pdf );
  $len = strlen ( $buf );

  header ( "Content-type: application/pdf" );
  header ( "Content-Length: $len" );
  header ( "Content-Disposition: inline; filename=character.pdf" );
  print $buf;
}
