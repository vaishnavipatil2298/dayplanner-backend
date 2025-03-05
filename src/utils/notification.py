from plyer import notification


def send_notification(task):
    notification.notify(
        title =" Task Reminder"
        message =f+It's time to {task}"!
        timeout = 10
    )