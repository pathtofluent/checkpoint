# PathToFluent Checkpoint

An Anki add-on for cards you either did or didn't do: a chapter of a book, an audio lesson, a workout. There's no way to get them "wrong", but you still want Anki to bring them back for review.

Status: early. Not yet tested across Anki versions.

## What it does

- Cards of the note type `Task` skip "Show Answer" and show one **Complete** button instead of Again / Hard / Good / Easy.
- Complete is recorded as Easy the first time (so the card doesn't come back in ten minutes) and as Good after that. Both are adjustable in the add-on's config.
- **Tools > Add Task Cards** creates many cards at once from a pasted list or a numbered series such as "Lesson {n}" from 1 to 30.

The `Task` note type is created for you, with a Title and an optional Details field.

## One card a day

Give each series its own deck and its own options preset with New cards/day = 1 and Maximum reviews/day = 1. A due review then uses the day's slot; on a day with no review, you get the next new card.

## Install

Build the add-on (below) or download it from Releases, then in Anki: Tools > Add-ons > Install from file, and restart.

On AnkiMobile and AnkiDroid these cards show the usual four buttons; tap Good.

## Building

```
python3 tools/build.py         # writes dist/pathtofluent_checkpoint.ankiaddon
```

## The PathToFluent tools

| Tool | What it does |
|------|--------------|
| [Trailblazer](https://github.com/pathtofluent/trailblazer) | Turns a video and its subtitles into an Anki deck |
| [Waypoint](https://github.com/pathtofluent/waypoint) | Sorts sentence cards so the next one has exactly one unknown word |
| [Checkpoint](https://github.com/pathtofluent/checkpoint) | A single Complete button for chapter and lesson cards |
| [Scout](https://github.com/pathtofluent/scout) | Finds Netflix titles by country and original language |

## Licence

GNU AGPL v3 or later. See `LICENSE`.
