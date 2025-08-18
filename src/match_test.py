from tennis import match
import pickle

tennismatch = match.TennisMatch("Piet", "Klaas")
print(tennismatch.get_scoreboard("Piet"))
serializematch = pickle.dumps(tennismatch)


loaded_match = pickle.loads(serializematch)
loaded_match.win_point("Piet")


print(loaded_match.get_scoreboard("Piet"))
