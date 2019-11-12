from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework.decorators import api_view

from core.models import Text, Section, Paragraph
from core.views import log


# STAFF

@api_view(['GET'])
def parse_text(_, text_uid):
    log.debug(f'start, text_uid={text_uid}')
    try:
        text = Text.objects.get(uid=text_uid)
    except Text.DoesNotExist:
        log.debug(f'not found, request for text_uid={text_uid}')
        return JsonResponse({'error': 'text not found', 'text_uid': text_uid}, status=404)
    else:
        text.update_paragraph_entries()
        log.debug(f'successfully updated text_uid={text_uid}')
        return HttpResponseRedirect(redirect_to=reverse('text_info', args=[text_uid]))


@api_view(['GET'])
def add_section(_, section_uid):
    log.debug(f'start, section_uid={section_uid}')
    try:
        current = Section.objects.get(uid=section_uid)
    except Section.DoesNotExist:
        log.debug(f'not found, request for section_uid={section_uid}')
        return JsonResponse({'error': 'section not found', 'section_uid': section_uid}, status=404)
    else:
        current.add_sub()
        log.debug(f'done, add section to section_uid={section_uid}')
        return HttpResponseRedirect(redirect_to=reverse('section_view', args=[section_uid]))


@api_view(['GET'])
def paragraph_concat(request, paragraph_uid):
    mode = request.GET.get('mode', '')
    if mode not in ['prev', 'next']:
        log.debug(f'wrong mode option \"{mode}\"')
        return JsonResponse({'error': 'wrong mode option', 'options': 'prev, next'}, status=401)

    try:
        anchor_number = int(request.GET.get('number', ''))
    except ValueError:
        anchor_number = None

    log.debug(f'start, paragraph_uid={paragraph_uid}, mode={mode}, anchor_number={anchor_number}')
    try:
        paragraph = Paragraph.objects.get(uid=paragraph_uid)
    except Paragraph.DoesNotExist:
        log.debug(f'not found, request for paragraph_uid={paragraph_uid}')
        return JsonResponse({'error': 'paragraph not found', 'paragraph_uid': paragraph_uid}, status=404)
    else:
        with_prev = mode == 'prev'
        paragraph.concat(with_prev=with_prev)
        log.debug(f'done, paragraph_uid={paragraph_uid}')
        return HttpResponseRedirect(
            redirect_to='{url}#{number}'.format(
                url=reverse('section_view', args=[paragraph.section.uid]),
                number=paragraph.serial_number if not anchor_number else anchor_number)
        )


# PART

@api_view(['GET'])
def text_sections(_, text_uid):
    """
    Observe all section of text

    :param _: request
    :param text_uid: uid of text to observe
    :return: JsonResponse in form {text_uid, sections: [{id, parent}, ]}
    """
    log.debug(f'start, text_uid={text_uid}')
    parts = Section.build_json(Section.of_text(text_uid))
    log.debug(f'done, text_uid={text_uid}')
    return JsonResponse({'text_uid': text_uid, 'sections': parts}, status=200)


@api_view(['GET'])
def sub_sections(_, section_uid):
    """
    Observe sub-sections of given part

    :param _: request
    :param section_uid: id of part to observe
    :return: JsonResponse in form {section_id, sections: [{id, parent}, ]}
    """
    log.debug(f'start, part_id={section_uid}')
    parts = Section.build_json(Section.of_section(section_uid))
    log.debug(f'done, part_id={section_uid}')
    return JsonResponse({'section_id': section_uid, 'sections': parts}, status=200)
