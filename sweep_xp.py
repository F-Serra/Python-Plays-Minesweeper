import win32api, win32gui, win32ui, win32con
import numpy as np
import cv2
import time

w = 480
h = 384	
rows = 30
cols = 24
field = np.zeros([rows, cols])
no_mines = 99
mines_found = 0

def main():

	numbers = list()
	for i in range(1,9):
		img = cv2.imread(str(i)+".jpg")
		img = cv2.resize(img,(16,16))
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]
		numbers.append(img)
	numbers.append(np.zeros_like(numbers[0]))
	black = np.zeros_like(numbers[0])
	black[:] = 255
	numbers.append(black)	
	
	global field
	square_w = w/rows
	square_h = h/cols

	while True:
		img = grab_screen((15, 100, 15+w, 100+h))
		img2 = np.zeros_like(img)
		img = cv2.blur(img,(2,2))
		thresh = 230
		img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]
		for x in range(cols):
			img_cols = list()
			for y in range(rows):
				x1 = round(x*square_w)
				x2 = round((x+1)*square_w)
				y1 = round(y*square_h)
				y2 = round((y+1)*square_h)
				crop_img = img[x1:x2, y1:y2]
				nr = img_to_nr(crop_img,numbers)
				if not field[y][x] == 10:
					field[y][x] = nr
				else:
					nr = 10
				font = cv2.FONT_HERSHEY_SIMPLEX
				nr_str = form(nr)
				cv2.putText(img2[x1:x2, y1:y2], nr_str,(2,12), font, 0.4,(155,155,155),1,cv2.LINE_AA)	
	
		cv2.imshow("img",img)
		cv2.imshow("img2",img2)
		m = next_move()
		#print(m)
		
		if mines_found==no_mines:
			click_all_unknowns()
			print("SUCCES!")
			time.sleep(10)
			cv2.destroyAllWindows()
			break
		if win32api.GetAsyncKeyState(ord('Q')):
			cv2.destroyAllWindows()
			break
		if cv2.waitKey(25) & 0xFF == ord('q'):
			time.sleep(1)
			cv2.destroyAllWindows()		
			break

	#print(field)
	#cv2.imshow("little1",numbers[0])

def form(nr):
	if nr < 8:
		return str(nr+1)
	elif nr == 8:
		return "-"
	elif nr == 9:
		return ""
	else:
		return "X"

def next_move():
	global field
	global mines_found
	for x in range(24):
		for y in range(30):
			
			nr = field[y][x]
			if nr < 8:
				#get neighbours
				nbrs = list()
				if y-1>=0 and x-1>=0:
					nbrs.append([y-1,x-1,field[y-1][x-1]])
				if y-1>=0:
					nbrs.append([y-1,x,field[y-1][x]])
				if y-1>=0 and x+1<24:
					nbrs.append([y-1,x+1,field[y-1][x+1]])
				if x-1>=0:
					nbrs.append([y,x-1,field[y][x-1]])
				if x+1<24:	
					nbrs.append([y,x+1,field[y][x+1]])
				if y+1<30 and x-1>=0:
					nbrs.append([y+1,x-1,field[y+1][x-1]])
				if y+1<30:	
					nbrs.append([y+1,x,field[y+1][x]])
				if y+1<30 and x+1<24:
					nbrs.append([y+1,x+1,field[y+1][x+1]])
				#print("pos: ",x,y)
				#print(nbrs)
				#count mines
				#count unknowns
				mines = list()
				unknowns = list()
				for f in nbrs:
					if f[2]==10:
						mines.append(f)
					elif f[2]==8:
						unknowns.append(f)
				#if unknowns+mines == nr set all unknowns to mines
				if len(unknowns)+len(mines) == (nr+1):
					if not len(unknowns)==0:
						for uk in unknowns:
							field[uk[0]][uk[1]]=10
							mines_found +=1
							print("Mines found: ", mines_found, "/ 99")
						return 2
				#if mines = nr click all unknowns
				elif len(mines)==(nr+1):
					if not len(unknowns)==0:
						for uk in unknowns:
							click(uk[0], uk[1])
						return 1

	random_click()
	return 0

def random_click():
	x_r = np.random.randint(0,30)
	y_r = np.random.randint(0,24)
	while not field[x_r][y_r]==8:
		x_r = np.random.randint(0,30)
		y_r = np.random.randint(0,24)
	print("random_click!")
	click(x_r, y_r)

def click_all_unknowns():
	#print(field)
	for x in range(24):
		for y in range(30):
			nr = field[y][x]
			if nr==8:
				#print(x,y)
				click(y,x)

def img_to_nr(img, nrs):
	mse_l = list()
	for nr in nrs:
		mse_l.append(mse(img,nr))
	return mse_l.index(min(mse_l))

	
def mse(img1, img2):
     return np.square(img1 - img2).mean()

def click(x1,y1):
	x=16+x1*16+8
	y=100+y1*16+8
	win32api.SetCursorPos((x,y))
	time.sleep(0.001)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
	time.sleep(0.001)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
	time.sleep(0.001)

def grab_screen(region):

	hwin = win32gui.GetDesktopWindow()

	left, top, x2, y2 = region
	width = x2 - left + 1
	height = y2 - top + 1

	hwindc = win32gui.GetWindowDC(hwin)
	srcdc = win32ui.CreateDCFromHandle(hwindc)
	memdc = srcdc.CreateCompatibleDC()
	bmp = win32ui.CreateBitmap()
	bmp.CreateCompatibleBitmap(srcdc, width, height)
	memdc.SelectObject(bmp)
	memdc.BitBlt((0, 0), (width, height), srcdc, (left, top), win32con.SRCCOPY)
    
	signedIntsArray = bmp.GetBitmapBits(True)
	img = np.fromstring(signedIntsArray, dtype='uint8')
	img.shape = (height,width,4)

	srcdc.DeleteDC()
	memdc.DeleteDC()
	win32gui.ReleaseDC(hwin, hwindc)
	win32gui.DeleteObject(bmp.GetHandle())

	return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

if __name__ == '__main__':
	main()