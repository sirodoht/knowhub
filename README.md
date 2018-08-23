# KnowHub.app

> Distributed home for remote companies

## Development

```sh
python manage.py runserver
celery -A knowhub worker -P gevent -l debug
```

## Code Formatting

Run:
```
black . && isort -y && flake8
```

## Colors

* text black #101010
* orange #ffa918
* orange hover #fe9f00
* blue #0808ff
* grey footer #aab7c4
* grey for orange bg (ligher) #ffedcd
* grey text for white bg (darker) #828282
* grey for meta #9199a1
* grey light for border #e4e6e8
* green
  * dark #0d9086
  * light for bg #d5f4f2
* red #d65050

## License

© Fugue Stateless Ltd
