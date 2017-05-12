import clr
import os
import imp
import housedes
imp.reload(housedes)
clr.AddReference("Eto")
clr.AddReference("Rhino.UI")
from Rhino.UI import *
from Eto.Forms import Form, CheckBox, TableRow, TableCell, Drawable, GroupBox, BorderType, Panel, DynamicLayout, VerticalAlignment, TableLayout, ColorPicker,Dialog, Label, TextBox, StackLayout, StackLayoutItem, Orientation, Button, HorizontalAlignment, MessageBox, ProgressBar, ImageView, TextAlignment
from Eto.Drawing import *
import scriptcontext
import System
import Rhino
import rhinoscriptsyntax as rs
import time

def SetToRendered():
    views = rs.ViewNames()
    modes=rs.ViewDisplayModes()
    viewtype="Rendered"
    rs.EnableRedraw(False)
    if viewtype in modes:
        for view in views:
            rs.ViewDisplayMode(view, viewtype)


def Capture():
   view = scriptcontext.doc.Views.ActiveView
   bitmap = view.CaptureToBitmap()
   memoryStream = System.IO.MemoryStream()
   format = System.Drawing.Imaging.ImageFormat.Png
   System.Drawing.Bitmap.Save(bitmap, memoryStream, format)
   
   if memoryStream.Length != 0:
       box1.Image = Bitmap(memoryStream)
       memoryStream.Dispose()

def L(text):
	return Label(Text = text, VerticalAlignment = VerticalAlignment.Center, TextAlignment = TextAlignment.Right)

#Initialising form
form = Dialog[bool]()
form.Title = "Automated House Design"
form.Resizable = False

layout = TableLayout()
layout.Spacing = Size(5,5)
layout.Padding = Padding(10,10,10,10)

#Defining textboxes, progress bars and buttons
textBoxPop = TextBox()
textBoxCross = TextBox()
textBoxMutation = TextBox()
textBoxGeneration = TextBox()
progressBar = ProgressBar(Value = 0, MaxValue = 50)
addSelectedButton = Button(Text = "Add Selected to Favourites")
addReferenceButton = Button(Text = "Add reference image")
generateButton = Button(Text = "Generate")
favouritesArray = []
unwantedArray = []
#Defining boxes for images
box1 = ImageView()
box1.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

box2 = ImageView()
box2.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

box3 = ImageView()
box3.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

box4 = ImageView()
box4.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

box5 = ImageView()
box5.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

box6 = ImageView()
box6.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')

boxAddSelected = ImageView()
boxAddSelected.Image = Bitmap('C:/Users/pezz/Desktop/RMIT/capstone/images/box.png')


#Defining checkboxes for images
checkbox1 = CheckBox()
checkbox2 = CheckBox()
checkbox3 = CheckBox()
checkbox4 = CheckBox()
checkbox5 = CheckBox()
checkbox6 = CheckBox()


#Adding button functionality
def generateButton_click(sender, e): 
    SetToRendered()
    if 'image' in globals():
        #runs Manuel's code
        housedes.main(image[0],
            int(textBoxPop.Text) if textBoxPop.Text != "" else 30,
            float(textBoxCross.Text) if textBoxCross.Text != "" else 0.7,
            float(textBoxMutation.Text) if textBoxMutation.Text != "" else 0.3,
            int(textBoxGeneration.Text) if textBoxGeneration.Text != "" else 50)
        progressBar.Value = housedes.progressBar()
        

        Capture()
    else:
        MessageBox.Show("You must generate an image first")       
generateButton.Click += generateButton_click

def addReferenceButton_click(sender, e): 
    global image
    image = housedes.load_image()
    boxAddSelected.Image = Bitmap(image[1])
addReferenceButton.Click += addReferenceButton_click

#Add pictures to array if checkboxes are checked
def addSelectedButton_click(sender, e): 
    #adding to favourite array
    if checkbox1.Checked == True:
        favouritesArray.append(box1)
    if checkbox2.Checked == True:
        favouritesArray.append(box2)
    if checkbox3.Checked == True:
        favouritesArray.append(box3)
    if checkbox4.Checked == True:
        favouritesArray.append(box4)
    if checkbox5.Checked == True:
        favouritesArray.append(box5)
    if checkbox6.Checked == True:
        favouritesArray.append(box6)
    #adding to unwanted array
    if checkbox1.Checked == False:
        unwantedArray.append(box1)
    if checkbox2.Checked == False:
        unwantedArray.append(box2)
    if checkbox3.Checked == False:
        unwantedArray.append(box3)
    if checkbox4.Checked == False:
        unwantedArray.append(box4)
    if checkbox5.Checked == False:
        unwantedArray.append(box5)
    if checkbox6.Checked == False:
        unwantedArray.append(box6)
    #validation for checkboxes (at least 1 must be selected)
    if checkbox1.Checked == False and checkbox2.Checked == False and checkbox3.Checked == False and checkbox4.Checked == False and checkbox5.Checked == False and checkbox6.Checked == False:
        MessageBox.Show("You must select at least 1 checkbox")
    else:
        MessageBox.Show(str(favouritesArray))
        MessageBox.Show(str(unwantedArray))

addSelectedButton.Click += addSelectedButton_click

#Drawing objects to form
layout.Rows.Add(TableRow(TableCell(box1), TableCell(box2), TableCell(box3), TableCell(L("PopSize: ")), textBoxPop))
layout.Rows.Add(TableRow(TableCell(checkbox1), TableCell(checkbox2), TableCell(checkbox3)))
layout.Rows.Add(TableRow(TableCell(box4), TableCell(box5), TableCell(box6), TableCell(L("Crosover: ")), textBoxCross))
layout.Rows.Add(TableRow(TableCell(checkbox4), TableCell(checkbox5), TableCell(checkbox6)))
layout.Rows.Add(TableRow(TableCell(), TableCell(), TableCell(), TableCell(L("Mutation: ")), textBoxMutation))
layout.Rows.Add(TableRow(TableCell(), TableCell(), TableCell(), TableCell(L("Generation: ")), textBoxGeneration))
layout.Rows.Add(TableRow(TableCell(addSelectedButton)))
layout.Rows.Add(TableRow(TableCell(), TableCell(), TableCell(), TableCell(), TableCell(boxAddSelected)))
layout.Rows.Add(TableRow(TableCell(), TableCell(), TableCell(), TableCell(), TableCell(addReferenceButton)))
layout.Rows.Add(TableRow(TableCell(progressBar), TableCell(generateButton)))

form.Content = layout

form.DefaultButton = generateButton


result = form.ShowModal(RhinoEtoApp.MainWindow)
