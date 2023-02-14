import flet as ft
import cv2
import base64
import time

roi_xy_start = [0, 0]
roi_xy_end = [0, 0]
old_roi_xy_end = roi_xy_end

def main(page: ft.Page):
    
    global old_roi_xy_end



    page.title = "Image ROI Example"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 50
    page.update()
    
    #file_picker = ft.FilePicker()
    #page.overlay.append(file_picker)
    #page.update()
    
    filepick_button = ft.ElevatedButton("Open a image", on_click=lambda _: file_picker.pick_files(allow_multiple=True))
    
    def on_dialog_result(e: ft.FilePickerResultEvent):
        print("Selected files:", e.files)
        print("Selected file or directory:", e.path)

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()
    
    page.add(filepick_button)
    
    def resize_img(img, frame_size=700):
        h, w, _ = img.shape
        aspect = h/w
        if h >= w:
            nh = frame_size
            nw = int(frame_size/aspect)
        else:
            nh = int(frame_size*aspect)
            nw = frame_size
        img = cv2.resize(img, (nw, nh))
        return img, nh, nw
    
    def get_img_base64(img):
        _, encoded = cv2.imencode(".jpg", img)
        img_base64 = base64.b64encode(encoded).decode("ascii")
        return img_base64
    
    img_path = "images/udon.jpg"
    img = cv2.imread(img_path)
    img, nh, nw = resize_img(img)
    img_base64 = get_img_base64(img)

    def image_ROI_start(e: ft.HoverEvent):
        global roi_xy_start
        roi_xy_start = int(e.local_x), int(e.local_y)
        print("ROI start:", roi_xy_start)
        
        
    def image_ROI_end(e: ft.HoverEvent):
        global roi_xy_end
        roi_xy_end = int(e.local_x), int(e.local_y)
        #print("ROI end:", e.local_x, e.local_y)
    
    gd = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.MOVE,
        #on_hover=on_enter_result,
        on_horizontal_drag_start=image_ROI_start,
        on_horizontal_drag_update=image_ROI_end,
    )

    frame = ft.Image(
        src_base64=img_base64,
        width=nw,
        height=nh,
        fit=ft.ImageFit.CONTAIN,
    )

    stack = ft.Stack([frame, gd], width=nw, height=nh)
    page.add(stack)
    
    old_file_picker_result = file_picker.result
    
    while True:
        
        if file_picker.result != old_file_picker_result:
            old_file_picker_result = file_picker.result
            
            img_path = file_picker.result.files[0].path
            img = cv2.imread(img_path)
            img, nh, nw = resize_img(img)
            img_base64 = get_img_base64(img)
            frame.src_base64 = img_base64
            print(nw, nh)
            frame.width = nw
            frame.height = nh
            stack.width = nw
            stack.height = nh
            page.update()
        
        if old_roi_xy_end != roi_xy_end:
            print("ROI area:", roi_xy_start, roi_xy_end)
            old_roi_xy_end = roi_xy_end
            
            img = cv2.imread(img_path)
            img, _, _ = resize_img(img)
            img = cv2.rectangle(img,
                                pt1=roi_xy_start,
                                pt2=roi_xy_end,
                                color=(255, 0, 0),
                                thickness=1)
            
            img_base64 = get_img_base64(img)
            frame.src_base64 = img_base64
            page.update()
            
            
            
        
        time.sleep(0.1)



ft.app(target=main)