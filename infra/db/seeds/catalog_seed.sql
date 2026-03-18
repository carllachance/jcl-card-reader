INSERT INTO catalog_cards (year, set_name, card_number, player_name, team, image_embedding)
VALUES
  (1989, 'Upper Deck', '1', 'Ken Griffey Jr.', 'Seattle Mariners', '[0.8,0.3,0.2]'),
  (1993, 'SP Foil', '279', 'Derek Jeter', 'New York Yankees', '[0.2,0.8,0.4]'),
  (2011, 'Topps Update', 'US175', 'Mike Trout', 'Los Angeles Angels', '[0.4,0.2,0.9]'),
  (2018, 'Topps Chrome', '150', 'Shohei Ohtani', 'Los Angeles Angels', '[0.6,0.7,0.3]'),
  (2020, 'Bowman', 'BP-50', 'Julio Rodriguez', 'Seattle Mariners', '[0.5,0.5,0.5]')
ON CONFLICT DO NOTHING;
