import json

import numpy as np
import whisperx
from fuzzywuzzy import fuzz
from tokenize_uk import tokenize_sents

MIN_THRESH = 60

def whisperx_alignment(audio_file: str, text_file: str, device = "cuda", batch_size = 16, compute_type = "float16", output_file = None):
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)

    audio = whisperx.load_audio(audio_file)
    result = model.transcribe(audio, batch_size=batch_size)

    segments = result['segments']

    with open(text_file, "r") as file:
        real_text = file.read()

    oneline_text = real_text.replace("\n", " ")
    splitted_real_text_sents = tokenize_sents(oneline_text)

    aligned_data = []

    sents_alignment = []
    for real_sent in splitted_real_text_sents:
        segment_scores = np.zeros(len(segments))
        segment_sents = np.zeros(len(segments))
        for segment_num, segment in enumerate(segments):
            segment_pred_text = segment["text"]
            segment_pred_text_splitted = tokenize_sents(segment_pred_text)
            sentences_scores = np.zeros(len(segment_pred_text_splitted))
            for sentence_num, sentence in enumerate(segment_pred_text_splitted):
                sentences_scores[sentence_num] = fuzz.ratio(real_sent, sentence)
            segment_scores[segment_num] = np.max(sentences_scores)
            segment_sents[segment_num] = np.argmax(sentences_scores)
        best_segment = segment_scores.argmax()
        best_sent = segment_sents[best_segment]
        best_segment_score = segment_scores[best_segment]

        if best_segment_score < MIN_THRESH:
            sents_alignment.append({
                "text": real_sent, 
                "segment_text": None,
                "score": None,
                "segment_num": None,
                "sentence_num": None
                })
        else:
            sents_alignment.append({
                "text": real_sent, 
                "segment_text": segments[best_segment]["text"],
                "score": best_segment_score,
                "segment_num": best_segment,
                "sentence_num": best_sent
                })

    for segment in segments:
        aligned_data.append({
            "text": "",
            "start": segment["start"],
            "end": segment["end"],
            "confidence_score": 1
        })

    for sentence_info in sents_alignment:
        if sentence_info["score"]:
            segment_num = sentence_info["segment_num"]
            aligned_data[segment_num]["text"] += sentence_info["text"]
            aligned_data[segment_num]["confidence_score"] *= sentence_info["score"]/100

    if output_file:
        with open(output_file, "w") as file:
            file_content = json.dumps(aligned_data, ensure_ascii=False)
            file_content = file_content.replace("{", "{\n")
            file_content = file_content.replace("}", "}\n")
            file_content = file_content.replace("\",", "\",\n")
            file.write(file_content)
    
    return aligned_data


if __name__ == '__main__':
    whisperx_alignment("./sample_alignment/sample_audio.wav", 
                       "./sample_alignment/sample_text.txt", 
                       output_file="./sample_alignment/sample_alignment.json")
