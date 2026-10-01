from server.src.collectors.icalendar_collector import get_events_on_date
from server.src.collectors.task_collector import collect_tasks
from server.src.collectors.weather_forecast import get_daily_forecast
# import utils.output_processing as op




from datetime import date, time, datetime


def stringPrint(output: str, ending: str):
    return output + (ending + "\n")

output = ""


DATE = date.today()




output = stringPrint(output, DATE.strftime("%A, %B %C"))
output = stringPrint(output=output, ending=get_daily_forecast())





events = get_events_on_date(DATE)
events.sort(key=lambda event: event.decoded("DTSTART").time() if type(event.decoded("DTSTART")) == datetime else time())

for event in events:
    output = stringPrint(output, "")
    output = stringPrint(output, event.get("SUMMARY"))

    if type(event.decoded("DTSTART")) == datetime:
        output = stringPrint(output, event.decoded("DTSTART").time().strftime("%I:%M").lstrip('0') + " - " +
              event.decoded("DTEND").time().strftime("%I:%M").lstrip('0'))




task_paths = [r"/Users/kevinsebastian/Library/Mobile Documents/iCloud~md~obsidian/Documents/Obsidian_Vault/"]

tasks = collect_tasks(
    task_paths,
    priorities=None,
    scheduled_before=DATE,
)

for task in tasks:
    output = stringPrint(output, "")
    due = f"Due: {task.due_date}" if task.due_date else ""
    priority = task.priority
    output = stringPrint(output, 
        f"{str(task.file).split("/")[-1].rstrip(".md")}: "
        f"{task.text} [{priority}] {due}"
    )





print(output)


output_file = "output/output"
with open(output_file, "wb") as f:
    f.write(bytes(output, 'utf-8'))

#with open(output_file, "rb") as f:
    #op.printBytes(f.read())





