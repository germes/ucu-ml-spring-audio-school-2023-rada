import json
from typing import List

import aeneas.globalconstants as gc
from aeneas.executetask import ExecuteTask
from aeneas.language import Language
from aeneas.syncmap import SyncMapFormat
from aeneas.task import Task, TaskConfiguration
from aeneas.textfile import TextFile, TextFragment


def forced_alignment(text: List[str], 
                     audio_path: str, 
                     language=Language.UKR, 
                     verbose=False, 
                     syncmap_path=None):
    config = TaskConfiguration()
    config[gc.PPN_TASK_LANGUAGE] = language
    config[gc.PPN_TASK_OS_FILE_FORMAT] = SyncMapFormat.JSON

    task = Task()
    task.configuration = config
    task.audio_file_path_absolute = audio_path

    text_file = TextFile()
    text_file.set_language(language)
    for i, line in enumerate(text):
        text_file.add_fragment(TextFragment(identifier=f"f{i:06d}", lines=[line], filtered_lines=[line], language=language))

    task.text_file = text_file

    ExecuteTask(task).execute()

    if syncmap_path:
        task.sync_map_file_path_absolute = syncmap_path
        task.output_sync_map_file()
        print(syncmap_path)
        with open(syncmap_path, 'r') as j:
            syncmap = json.loads(j.read())
            syncmap_object = json.dumps(syncmap, ensure_ascii=False)
            syncmap_object = syncmap_object.replace("{", "{\n")
            syncmap_object = syncmap_object.replace("}", "}\n")
            syncmap_object = syncmap_object.replace("\",", "\",\n")

        with open(syncmap_path, 'w') as j:
            j.write(syncmap_object)

    if verbose:
        for leave in task.sync_map_leaves():
            print(f'Fragment {leave.identifier:10s}: Text ', end='')
            print(leave.text.encode('utf-8'), end='')
            print(f' ({leave.chars} chars); timing {leave.begin:.2f}-{leave.end:.2f} ({leave.length:.2f} sec)')
    
    alignments_list = [{"id": leave.identifier, 
                        "text": leave.text, 
                        "start_time": leave.begin, 
                        "end_time": leave.end} for leave in task.sync_map_leaves()]

    return alignments_list

if __name__ == '__main__':
    audio_file_path = "./sample_alignment/sample_alignment.wav"
    text_file_path = "./sample_alignment/sample_alignment.txt"
    with open(text_file_path, "r") as text_file:
        text = text_file.read()
    splitted_text = text.split("\n")

    forced_alignment(splitted_text, audio_file_path, 
                     syncmap_path="./sample_alignment/sample_alignment_aeneas.json", verbose=True)
