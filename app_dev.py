import flet as ft
import cv2
import base64
import numpy as np

roi_xy_start = [0, 0]
roi_xy_end = [0, 0]
old_roi_xy_end = roi_xy_end

def main(page: ft.Page):
    global img_as_read

    img = 255*np.ones((300, 300, 3), dtype="uint8")
    img = cv2.putText(img, "Original Image", (25, 270), color=(255, 0, 0), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale=2, 
                    thickness=3,
                    lineType=cv2.LINE_AA)
    img_original = img
    
    img = 255*np.ones((300, 300, 3), dtype="uint8")
    img = cv2.putText(img, "ROI Image", (100, 270), color=(255, 0, 0), 
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, 
                    fontScale=2, 
                    thickness=3,
                    lineType=cv2.LINE_AA)
    img_cropped = img

    page.title = "Image ROI Example"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 50

    

    def roi_img(e):
        print("do ROI")
        print(roi_xy_start, roi_xy_end)
        x_list = np.array([roi_xy_start[0], roi_xy_end[0]])
        y_list = np.array([roi_xy_start[1], roi_xy_end[1]])
        x0 = x_list.min()
        x1 = x_list.max()
        y0 = y_list.min()
        y1 = y_list.max()
        img, _, _ = resize_img(img_as_read)
        img_sliced = img[y0:y1, x0:x1,:]
        img_base64 = get_img_base64(img_sliced)
        frame2.src_base64 = img_base64
        page.update()

    filepick_button = ft.ElevatedButton("Open Image", on_click=lambda _: file_picker.pick_files(allow_multiple=True))
    roi_button = ft.ElevatedButton("ROI", on_click=roi_img)
    
    page.add(ft.Row([filepick_button, roi_button]))
    
    img_filepath_text = ft.Text("Please open an image.")
    
    page.add(img_filepath_text)
    
    def on_dialog_result(e: ft.FilePickerResultEvent):
        global img_path, img_as_read, roi_xy_start, roi_xy_end
        print("Selected files:", e.files)
        print("Selected file or directory:", e.path)
        img_path = e.files[0].path
        img_filepath_text.value = img_path
        img_as_read = cv2.imread(img_path)
        img, nh, nw = resize_img(img_as_read)
        img_base64 = get_img_base64(img)
        frame.src_base64 = img_base64
        print(nw, nh)
        frame.width = nw
        frame.height = nh
        stack.width = nw
        stack.height = nh
        roi_xy_start = (0,0)
        roi_xy_end = (0, 0)
        page.update()
    

    file_picker = ft.FilePicker(on_result=on_dialog_result)
    page.overlay.append(file_picker)
    page.update()
    
    
    
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
    

    def image_ROI_start(e: ft.HoverEvent):
        global roi_xy_start
        roi_xy_start = int(e.local_x), int(e.local_y)
        print("ROI start:", roi_xy_start)
        
        
    def image_ROI_end(e: ft.HoverEvent):
        global roi_xy_end, img_as_read
        roi_xy_end = int(e.local_x), int(e.local_y)
        print("ROI end:", roi_xy_end)
        img, _, _ = resize_img(img_as_read)
        img = cv2.rectangle(img,
                            pt1=roi_xy_start,
                            pt2=roi_xy_end,
                            color=(255, 255, 0),
                            thickness=1)
        img_base64 = get_img_base64(img)
        frame.src_base64 = img_base64
        page.update()
        
    def show_roi_guide(e: ft.HoverEvent):
        global img_as_read
        mouse_x = int(e.local_x)
        mouse_y = int(e.local_y)
        print(mouse_x, mouse_y)
        img, _, _ = resize_img(img_as_read)
        img = cv2.rectangle(img,
                            pt1=roi_xy_start,
                            pt2=roi_xy_end,
                            color=(255, 255, 0),
                            thickness=1)
        img = cv2.line(img,
                        pt1=(mouse_x, mouse_y-50),
                        pt2=(mouse_x, mouse_y+50),
                        color=(255, 255, 0),
                        thickness=1)
        img = cv2.line(img,
                        pt1=(mouse_x-50, mouse_y),
                        pt2=(mouse_x+50, mouse_y),
                        color=(255, 255, 0),
                        thickness=1)
        
        img_base64 = get_img_base64(img)
        frame.src_base64 = img_base64
        page.update()

    img_path = None
    img_as_read = img_original
    img, nh, nw = resize_img(img_as_read)
    img_base64 = get_img_base64(img)
    
    print(img_path, nh, nw)
    print(img_as_read)

   
    gd = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.MOVE,
        on_hover=show_roi_guide,
        on_horizontal_drag_start=image_ROI_start,
        on_horizontal_drag_update=image_ROI_end,
    )

    frame = ft.Image(
        src_base64=img_base64,
        width=nw,
        height=nh,
        fit=ft.ImageFit.CONTAIN,
    )

    img, nh, nw = resize_img(img_cropped)
    img_base64 = get_img_base64(img)
    
    frame2 = ft.Image(
        src_base64=img_base64,
        width=nw,
        height=nh,
        fit=ft.ImageFit.CONTAIN,
    )

    stack = ft.Stack([frame, gd], width=nw, height=nh)
    page.add(ft.Row([stack, frame2]))
    page.update()
   



ft.app(target=main)