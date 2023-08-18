#!/usr/bin/python3
import unittest

from main import normalize_title

class TestNormalization(unittest.TestCase):

    def iterate_pairs(self, examples):
        print(examples)
        for key, value in examples.items():
            key = normalize_title(key)
            value = normalize_title(value)
            self.assertEqual(key, value)

    def test_date(self):
        movies_with_dates = {
            "Spaceballs (1987)": "Spaceballs",
            "Toy Story(1995)": "Toy Story",
            "1984(1984)": "1984 (1984)",
        }
        self.iterate_pairs(movies_with_dates)
    
    def test_capitalization(self):
        movies_with_capitalization = {
            "WALL-E": "wall-e",
            "Snow White and the Seven Dwarfs": "Snow white and the seven dwarfs",
            "SpaceBalls": "Spaceballs",
        }
        self.iterate_pairs(movies_with_capitalization)
        
    def test_umlauts(self):
        movies_with_umlauts = {
            "Und täglich grüßt das Murmeltier": "Und taeglich gruesst das Murmeltier"
        }
        self.iterate_pairs(movies_with_umlauts)
        
    def test_parenthesis_o(self):
        movies_with_parenthesis_o = {
            "Nymph()maniac": "Nymphomaniac",
        }
        self.iterate_pairs(movies_with_parenthesis_o)
        
    def test_accents(self):
        movies_with_accents = {
            "Amélie": "Amelie",
            "Là-haut": "La-haut",
            "Ève": "Eve",
        }
        self.iterate_pairs(movies_with_accents)
        
    def test_special_characters(self):
        movies_with_special_characters = {
            "Wallace & Gromit": "Wallace und Gromit",
            "Star Wars Episode III — Revenge of the Sith": "Star Wars Episode III - Revenge of the Sith",
            "Rogue One: A Star Wars Story": "Rogue One A Star Wars Story",
            "Solo: A Star Wars Story": "Solo - A Star Wars Story",
            "Super Mario Bros.": "Super Mario Bros",
        }
        self.iterate_pairs(movies_with_special_characters)
    
    def test_fractions(self):
        movies_with_fractions = {
            "The Naked Gun 2 ½": "The naked Gun 2 1/2",
            "Naked Gun 33⅓": "Naked Gun 33 1-3",
        }
        self.iterate_pairs(movies_with_fractions)
        
    def test_complex_names(self):
        movies_with_complex_names = {
            "Jurassic World: Dominion (2022)": "Jurassic World Dominion",
            "Hot Shots! (1991)": "Hot Shots",
            "O Brother, Where Art Thou? (2000)": "O Brother where art thou",
            " Naked Gun 33⅓: The Final Insult (1994) ": "Naked Gun 33 1/3 The Final Insult"
        }
        self.iterate_pairs(movies_with_complex_names)
        
if __name__ == '__main__':
    unittest.main()