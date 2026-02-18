from concurrent.futures import as_completed


def handle_futures(futures, stdout, style):
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            stdout.write(style.ERROR(f"Error occurred: {e}"))
