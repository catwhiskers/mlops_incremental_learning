object_categories = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 
                     'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 
                     'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
object_categories_dict = {str(i): j for i, j in enumerate(object_categories)}

def convert_a2i_to_augmented_manifest(a2i_output):
    annotations = []
    confidence = []
    for i, bbox in enumerate(a2i_output['humanAnswers'][0]['answerContent']['annotatedResult']['boundingBoxes']):
        object_class_key = [key for (key, value) in object_categories_dict.items() if value == bbox['label']][0]
        obj = {'class_id': int(object_class_key), 
               'width': bbox['width'],
               'top': bbox['top'],
               'height': bbox['height'],
               'left': bbox['left']}
        annotations.append(obj)
        confidence.append({'confidence': 1})

    # We set "a2i-retraining" as the attribute name for this dataset. This will later be used in setting the training data
    augmented_manifest={'source-ref': a2i_output['inputContent']['taskObject'],
                        'a2i-retraining': {'annotations': annotations,
                                           'image_size': [{'width': a2i_output['humanAnswers'][0]['answerContent']['annotatedResult']['inputImageProperties']['width'],
                                                           'depth':3,
                                                           'height': a2i_output['humanAnswers'][0]['answerContent']['annotatedResult']['inputImageProperties']['height']}]},
                        'a2i-retraining-metadata': {'job-name': 'a2i/%s' % a2i_output['humanLoopName'],
                                                    'class-map': object_categories_dict,
                                                    'human-annotated':'yes',
                                                    'objects': confidence,
                                                    'creation-date': a2i_output['humanAnswers'][0]['submissionTime'],
                                                    'type':'groundtruth/object-detection'}}
    return augmented_manifest