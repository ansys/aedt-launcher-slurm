# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jul 19 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui
import wx.dataview
import wx.grid

###########################################################################
## Class GUIFrame
###########################################################################

class GUIFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"AEDT Launcher", pos = wx.DefaultPosition, size = wx.Size( 1395,882 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )
		self.m_mgr = wx.aui.AuiManager()
		self.m_mgr.SetManagedWindow( self )
		self.m_mgr.SetFlags(wx.aui.AUI_MGR_DEFAULT|wx.aui.AUI_MGR_LIVE_RESIZE|wx.aui.AUI_MGR_NO_VENETIAN_BLINDS_FADE)
		
		self.m_notebook2 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.NB_NOPAGETHEME )
		self.m_notebook2.SetMinSize( wx.Size( 400,400 ) )
		
		self.m_mgr.AddPane( self.m_notebook2, wx.aui.AuiPaneInfo() .Left() .Caption( u"AEDT Launcher for Ottsimportal2" ).CaptionVisible( False ).CloseButton( False ).Dock().Resizable().FloatingSize( wx.DefaultSize ).Floatable( False ).CentrePane() )
		
		self.m_panel2 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel2.SetMinSize( wx.Size( 400,-1 ) )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText7 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"AEDT Launcher for Ottsimportal2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )
		
		self.m_staticText7.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )
		
		m_radioBox1Choices = [ u"Pre- / Postprocessing", u"Interactive Session" ]
		self.m_radioBox1 = wx.RadioBox( self.m_panel2, wx.ID_ANY, u"Mode", wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
		self.m_radioBox1.SetSelection( 0 )
		bSizer14.Add( self.m_radioBox1, 0, wx.ALL, 5 )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		PESizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText12 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Parallel Env.", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )
		
		self.m_staticText12.SetMinSize( wx.Size( 100,-1 ) )
		
		PESizer.Add( self.m_staticText12, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		m_select_peChoices = [ u"electronics-8", u"electronics-16", u"electronics-28" ]
		self.m_select_pe = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_select_peChoices, wx.CB_READONLY )
		self.m_select_pe.SetSelection( 0 )
		self.m_select_pe.SetMinSize( wx.Size( 150,-1 ) )
		
		PESizer.Add( self.m_select_pe, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( PESizer, 0, wx.ALL, 5 )
		
		CoreSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText122 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Num. Cores", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText122.Wrap( -1 )
		
		self.m_staticText122.SetMinSize( wx.Size( 100,-1 ) )
		
		CoreSizer.Add( self.m_staticText122, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_numcore = wx.TextCtrl( self.m_panel2, wx.ID_ANY, u"8", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_numcore.SetMinSize( wx.Size( 50,-1 ) )
		
		bSizer13.Add( self.m_numcore, 0, wx.ALL, 5 )
		
		self.m_node_label = wx.StaticText( self.m_panel2, wx.ID_ANY, u"(28 cores, 512GB  / node)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_node_label.Wrap( -1 )
		
		bSizer13.Add( self.m_node_label, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		CoreSizer.Add( bSizer13, 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( CoreSizer, 0, wx.ALL, 5 )
		
		bSizer15 = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizer15.Add( ( 60, 0), 1, wx.FIXED_MINSIZE, 5 )
		
		self.m_checkBox2 = wx.CheckBox( self.m_panel2, wx.ID_ANY, u"Exclusive", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox2.SetMinSize( wx.Size( 80,-1 ) )
		
		bSizer15.Add( self.m_checkBox2, 0, wx.ALL, 5 )
		
		
		bSizer15.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		bSizer7.Add( bSizer15, 1, wx.EXPAND, 5 )
		
		
		bSizer14.Add( bSizer7, 0, wx.ALL, 5 )
		
		bSizer71 = wx.BoxSizer( wx.VERTICAL )
		
		VersionSizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_version_text1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"AEDT Version", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_version_text1.Wrap( -1 )
		
		self.m_version_text1.SetMinSize( wx.Size( 80,-1 ) )
		
		VersionSizer1.Add( self.m_version_text1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		m_select_version1Choices = [ u"R18.2", u"R19.0", u"R19.1", u"R19.2", u"v2019 R1" ]
		self.m_select_version1 = wx.ComboBox( self.m_panel2, wx.ID_ANY, u"R19.0", wx.DefaultPosition, wx.Size( -1,-1 ), m_select_version1Choices, wx.CB_READONLY|wx.CB_SORT )
		self.m_select_version1.SetSelection( 4 )
		self.m_select_version1.SetMinSize( wx.Size( 150,-1 ) )
		
		VersionSizer1.Add( self.m_select_version1, 0, wx.ALL, 5 )
		
		self.m_button1 = wx.Button( self.m_panel2, wx.ID_ANY, u"Launch AEDT", wx.DefaultPosition, wx.DefaultSize, 0 )
		VersionSizer1.Add( self.m_button1, 0, wx.ALL, 5 )
		
		
		bSizer71.Add( VersionSizer1, 0, wx.ALL, 5 )
		
		PESizer1 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText121 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Options", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText121.Wrap( -1 )
		
		self.m_staticText121.SetMinSize( wx.Size( 80,-1 ) )
		
		PESizer1.Add( self.m_staticText121, 0, wx.ALIGN_TOP|wx.ALL, 5 )
		
		self.m_OptionsText = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_LEFT|wx.TE_MULTILINE )
		self.m_OptionsText.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_OptionsText.Enable( False )
		self.m_OptionsText.SetMinSize( wx.Size( 500,65 ) )
		
		PESizer1.Add( self.m_OptionsText, 0, wx.ALIGN_TOP|wx.ALL, 5 )
		
		self.m_checkBox1 = wx.CheckBox( self.m_panel2, wx.ID_ANY, u"Edit", wx.DefaultPosition, wx.DefaultSize, 0 )
		PESizer1.Add( self.m_checkBox1, 0, wx.ALL, 5 )
		
		
		bSizer71.Add( PESizer1, 1, wx.ALL, 5 )
		
		
		bSizer14.Add( bSizer71, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( bSizer14, 0, wx.ALL, 5 )
		
		self.m_staticline12 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.page_Data = wx.Panel( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.page_Data.SetMinSize( wx.Size( -1,500 ) )
		
		bSizer8.Add( self.page_Data, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizer141 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_dataViewListCtrl1 = wx.dataview.DataViewListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_dataViewListCtrl1.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_dataViewListCtrl1.SetMinSize( wx.Size( 800,250 ) )
		
		bSizer141.Add( self.m_dataViewListCtrl1, 0, wx.ALL, 5 )
		
		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText8 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Scheduler Messages", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )
		
		bSizer16.Add( self.m_staticText8, 0, wx.ALL, 5 )
		
		
		bSizer16.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_checkBox_allmsg = wx.CheckBox( self.m_panel2, wx.ID_ANY, u"All Messages", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.m_checkBox_allmsg, 0, wx.ALL, 5 )
		
		
		bSizer141.Add( bSizer16, 0, wx.EXPAND, 5 )
		
		self.m_dataViewListCtrl2 = wx.dataview.DataViewListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_HORIZ_RULES|wx.dataview.DV_NO_HEADER|wx.dataview.DV_ROW_LINES|wx.dataview.DV_VARIABLE_LINE_HEIGHT|wx.HSCROLL|wx.VSCROLL )
		self.m_dataViewListCtrl2.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.m_dataViewListCtrl2.SetMinSize( wx.Size( 800,200 ) )
		
		bSizer141.Add( self.m_dataViewListCtrl2, 0, wx.ALL, 5 )
		
		
		bSizer8.Add( bSizer141, 1, wx.EXPAND, 5 )
		
		
		bSizer1.Add( bSizer8, 1, wx.EXPAND, 5 )
		
		self.m_staticline11 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )
		
		ButtonSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		
		ButtonSizer.Add( ( 0, 0), 1, 0, 5 )
		
		self.m_button2 = wx.Button( self.m_panel2, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		ButtonSizer.Add( self.m_button2, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( ButtonSizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_TOP, 5 )
		
		
		self.m_panel2.SetSizer( bSizer1 )
		self.m_panel2.Layout()
		bSizer1.Fit( self.m_panel2 )
		self.m_notebook2.AddPage( self.m_panel2, u"Launcher", True )
		self.m_panel3 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer23 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText9 = wx.StaticText( self.m_panel3, wx.ID_ANY, u"User-specific builds", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText9.Wrap( -1 )
		
		bSizer23.Add( self.m_staticText9, 0, wx.ALL, 5 )
		
		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_grid2 = wx.grid.Grid( self.m_panel3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.m_grid2.CreateGrid( 1, 2 )
		self.m_grid2.EnableEditing( True )
		self.m_grid2.EnableGridLines( True )
		self.m_grid2.EnableDragGridSize( False )
		self.m_grid2.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid2.SetColSize( 0, 100 )
		self.m_grid2.SetColSize( 1, 600 )
		self.m_grid2.EnableDragColMove( False )
		self.m_grid2.EnableDragColSize( True )
		self.m_grid2.SetColLabelSize( 20 )
		self.m_grid2.SetColLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid2.EnableDragRowSize( True )
		self.m_grid2.SetRowLabelSize( 80 )
		self.m_grid2.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid2.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.m_grid2.SetMinSize( wx.Size( -1,400 ) )
		
		bSizer17.Add( self.m_grid2, 0, wx.ALL, 5 )
		
		
		bSizer23.Add( bSizer17, 0, wx.EXPAND, 5 )
		
		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_button3 = wx.Button( self.m_panel3, wx.ID_ANY, u"Delete Selected Row", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_button3, 0, wx.ALL, 5 )
		
		self.m_button4 = wx.Button( self.m_panel3, wx.ID_ANY, u"Add Row", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.m_button4, 0, wx.ALL, 5 )
		
		
		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )
		
		
		bSizer23.Add( bSizer18, 1, wx.EXPAND, 5 )
		
		
		self.m_panel3.SetSizer( bSizer23 )
		self.m_panel3.Layout()
		bSizer23.Fit( self.m_panel3 )
		self.m_notebook2.AddPage( self.m_panel3, u"Builds", False )
		self.m_panel4 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook2.AddPage( self.m_panel4, u"Queues", False )
		
		self.m_grid1 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.m_grid1.CreateGrid( 5, 5 )
		self.m_grid1.EnableEditing( True )
		self.m_grid1.EnableGridLines( True )
		self.m_grid1.EnableDragGridSize( False )
		self.m_grid1.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid1.EnableDragColMove( False )
		self.m_grid1.EnableDragColSize( True )
		self.m_grid1.SetColLabelSize( 30 )
		self.m_grid1.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid1.EnableDragRowSize( True )
		self.m_grid1.SetRowLabelSize( 80 )
		self.m_grid1.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid1.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		self.m_mgr.AddPane( self.m_grid1, wx.aui.AuiPaneInfo() .Left() .PinButton( True ).Hide().Dock().Resizable().FloatingSize( wx.DefaultSize ) )
		
		self.m_statusBar1 = self.CreateStatusBar( 2, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.m_statusBar1.SetMinSize( wx.Size( 180,-1 ) )
		
		
		self.m_mgr.Update()
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_CLOSE, self.shutdown_app )
		self.m_radioBox1.Bind( wx.EVT_RADIOBOX, self.select_mode )
		self.m_select_pe.Bind( wx.EVT_COMBOBOX, self.select_pe )
		self.m_button1.Bind( wx.EVT_BUTTON, self.click_launch )
		self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self.m_check_edit )
		self.m_dataViewListCtrl1.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.leftclick_processtable, id = wx.ID_ANY )
		self.m_checkBox_allmsg.Bind( wx.EVT_CHECKBOX, self.m_update_msg_list )
		self.m_button2.Bind( wx.EVT_BUTTON, self.click_cancel )
		self.m_grid2.Bind( wx.grid.EVT_GRID_CELL_CHANGED, self.edit_cell )
		self.m_button3.Bind( wx.EVT_BUTTON, self.delete_row )
		self.m_button4.Bind( wx.EVT_BUTTON, self.add_row )
	
	def __del__( self ):
		self.m_mgr.UnInit()
		
	
	
	# Virtual event handlers, overide them in your derived class
	def shutdown_app( self, event ):
		event.Skip()
	
	def select_mode( self, event ):
		event.Skip()
	
	def select_pe( self, event ):
		event.Skip()
	
	def click_launch( self, event ):
		event.Skip()
	
	def m_check_edit( self, event ):
		event.Skip()
	
	def leftclick_processtable( self, event ):
		event.Skip()
	
	def m_update_msg_list( self, event ):
		event.Skip()
	
	def click_cancel( self, event ):
		event.Skip()
	
	def edit_cell( self, event ):
		event.Skip()
	
	def delete_row( self, event ):
		event.Skip()
	
	def add_row( self, event ):
		event.Skip()
	

