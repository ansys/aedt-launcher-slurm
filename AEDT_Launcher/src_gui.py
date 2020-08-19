# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.9.0 Feb 17 2020)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui
import wx.grid
import wx.dataview

###########################################################################
## Class GUIFrame
###########################################################################

class GUIFrame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"AEDT Launcher", pos = wx.DefaultPosition, size = wx.Size( 1300,882 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

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

		self.title_caption = wx.StaticText( self.m_panel2, wx.ID_ANY, u"AEDT Launcher", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.title_caption.Wrap( -1 )

		self.title_caption.SetFont( wx.Font( 14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )

		bSizer1.Add( self.title_caption, 0, wx.ALL, 5 )

		self.m_staticline1 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer261 = wx.BoxSizer( wx.VERTICAL )

		submit_mode_radioboxChoices = [ u"Pre- / Postprocessing", u"Interactive Session" ]
		self.submit_mode_radiobox = wx.RadioBox( self.m_panel2, wx.ID_ANY, u"Mode", wx.DefaultPosition, wx.DefaultSize, submit_mode_radioboxChoices, 1, wx.RA_SPECIFY_COLS )
		self.submit_mode_radiobox.SetSelection( 1 )
		bSizer261.Add( self.submit_mode_radiobox, 0, wx.ALL, 5 )


		bSizer14.Add( bSizer261, 1, wx.EXPAND, 5 )

		bSizer7 = wx.BoxSizer( wx.VERTICAL )

		QueueSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Queue", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText1.Wrap( -1 )

		self.m_staticText1.SetMinSize( wx.Size( 100,-1 ) )

		QueueSizer.Add( self.m_staticText1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		queue_dropmenuChoices = [ u"euc09", u"ottc01", u"euc09lm" ]
		self.queue_dropmenu = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), queue_dropmenuChoices, wx.CB_READONLY )
		self.queue_dropmenu.SetSelection( 1 )
		self.queue_dropmenu.SetMinSize( wx.Size( 150,-1 ) )

		QueueSizer.Add( self.queue_dropmenu, 0, wx.ALIGN_CENTER|wx.ALL|wx.RIGHT, 5 )


		bSizer7.Add( QueueSizer, 0, wx.ALL, 5 )

		PESizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText12 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Parallel Env.", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		self.m_staticText12.SetMinSize( wx.Size( 100,-1 ) )

		PESizer.Add( self.m_staticText12, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		pe_dropmenuChoices = []
		self.pe_dropmenu = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, pe_dropmenuChoices, wx.CB_READONLY )
		self.pe_dropmenu.SetSelection( 0 )
		self.pe_dropmenu.SetMinSize( wx.Size( 150,-1 ) )

		PESizer.Add( self.pe_dropmenu, 0, wx.ALL, 5 )


		bSizer7.Add( PESizer, 0, wx.ALL, 5 )

		CoreSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText122 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Num. Cores", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText122.Wrap( -1 )

		self.m_staticText122.SetMinSize( wx.Size( 100,-1 ) )

		CoreSizer.Add( self.m_staticText122, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		bSizer13 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_numcore = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_numcore.SetMinSize( wx.Size( 50,-1 ) )

		bSizer13.Add( self.m_numcore, 0, wx.ALL, 5 )

		self.m_node_label = wx.StaticText( self.m_panel2, wx.ID_ANY, u"(28 cores, 512GB  / node)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_node_label.Wrap( -1 )

		bSizer13.Add( self.m_node_label, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		CoreSizer.Add( bSizer13, 1, wx.EXPAND, 5 )


		bSizer7.Add( CoreSizer, 0, wx.ALL, 5 )

		reserved_sizer = wx.BoxSizer( wx.HORIZONTAL )

		self.reserved_checkbox = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.reserved_checkbox.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.reserved_checkbox.SetMinSize( wx.Size( 20,-1 ) )
		self.reserved_checkbox.SetMaxSize( wx.Size( 20,-1 ) )

		reserved_sizer.Add( self.reserved_checkbox, 0, wx.ALL, 5 )

		self.m_staticText121111 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Reservation ID", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText121111.Wrap( -1 )

		self.m_staticText121111.SetMinSize( wx.Size( 90,-1 ) )

		reserved_sizer.Add( self.m_staticText121111, 0, wx.ALL, 5 )

		self.reservation_id_text = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_LEFT|wx.TE_MULTILINE )
		self.reservation_id_text.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.reservation_id_text.SetMinSize( wx.Size( 170,25 ) )
		self.reservation_id_text.SetMaxSize( wx.Size( 170,25 ) )

		reserved_sizer.Add( self.reservation_id_text, 0, wx.ALIGN_TOP|wx.ALL, 5 )


		bSizer7.Add( reserved_sizer, 1, wx.EXPAND, 5 )

		self.m_staticText18 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Specify Project Path:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )

		bSizer7.Add( self.m_staticText18, 0, wx.ALL, 5 )

		PESizer12 = wx.BoxSizer( wx.HORIZONTAL )

		self.path_textbox = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_LEFT|wx.TE_MULTILINE )
		self.path_textbox.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.path_textbox.Enable( False )
		self.path_textbox.SetMinSize( wx.Size( 300,30 ) )

		PESizer12.Add( self.path_textbox, 0, wx.ALIGN_TOP|wx.ALL, 5 )

		self.set_path_button = wx.Button( self.m_panel2, wx.ID_ANY, u"...", wx.DefaultPosition, wx.Size( 30,30 ), 0 )
		PESizer12.Add( self.set_path_button, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer7.Add( PESizer12, 0, wx.EXPAND, 5 )


		bSizer14.Add( bSizer7, 0, wx.ALL, 5 )

		bSizer71 = wx.BoxSizer( wx.VERTICAL )

		VersionSizer1 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_version_text1 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Version", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_version_text1.Wrap( -1 )

		self.m_version_text1.SetMinSize( wx.Size( 95,-1 ) )

		VersionSizer1.Add( self.m_version_text1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		m_select_version1Choices = []
		self.m_select_version1 = wx.ComboBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), m_select_version1Choices, wx.CB_READONLY )
		self.m_select_version1.SetSelection( 0 )
		self.m_select_version1.SetMinSize( wx.Size( 150,-1 ) )

		VersionSizer1.Add( self.m_select_version1, 0, wx.ALL, 5 )

		self.m_button1 = wx.Button( self.m_panel2, wx.ID_ANY, u"Launch", wx.DefaultPosition, wx.DefaultSize, 0 )
		VersionSizer1.Add( self.m_button1, 0, wx.ALL, 5 )


		bSizer71.Add( VersionSizer1, 0, wx.ALL, 5 )

		PESizer11 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText1211 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Environment variables", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText1211.Wrap( 1 )

		self.m_staticText1211.SetMinSize( wx.Size( 100,-1 ) )

		PESizer11.Add( self.m_staticText1211, 0, wx.ALIGN_TOP|wx.ALL, 5 )

		self.env_var_text = wx.TextCtrl( self.m_panel2, wx.ID_ANY, u"PRESERVE_SOLVER_FILES=0, SKIP_MESHCHECK=0", wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_LEFT|wx.TE_MULTILINE )
		self.env_var_text.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.env_var_text.SetToolTip( u"Format:\nVARIABLE_NAME1=VARIABLE_VALUE1,VARIABLE_NAME2=VARIABLE_VALUE2" )
		self.env_var_text.SetMinSize( wx.Size( 500,65 ) )

		PESizer11.Add( self.env_var_text, 0, wx.ALIGN_TOP|wx.ALL, 5 )


		bSizer71.Add( PESizer11, 1, wx.EXPAND, 5 )

		PESizer1 = wx.BoxSizer( wx.HORIZONTAL )

		self.advanced_checkbox = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.advanced_checkbox.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.advanced_checkbox.SetMinSize( wx.Size( 20,-1 ) )
		self.advanced_checkbox.SetMaxSize( wx.Size( 20,-1 ) )

		PESizer1.Add( self.advanced_checkbox, 0, wx.ALL, 5 )

		self.m_staticText12111 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Modify advanced options", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.m_staticText12111.Wrap( 1 )

		self.m_staticText12111.SetMinSize( wx.Size( 64,-1 ) )
		self.m_staticText12111.SetMaxSize( wx.Size( 64,-1 ) )

		PESizer1.Add( self.m_staticText12111, 0, wx.ALL, 5 )

		self.advanced_options_text = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CHARWRAP|wx.TE_LEFT|wx.TE_MULTILINE )
		self.advanced_options_text.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.advanced_options_text.SetMinSize( wx.Size( 500,65 ) )

		PESizer1.Add( self.advanced_options_text, 0, wx.ALIGN_TOP|wx.ALL, 5 )


		bSizer71.Add( PESizer1, 1, wx.ALL, 5 )


		bSizer14.Add( bSizer71, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer14, 0, wx.ALL, 5 )

		self.m_staticline12 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer1411 = wx.BoxSizer( wx.VERTICAL )

		self.load_grid = wx.grid.Grid( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.load_grid.CreateGrid( 0, 5 )
		self.load_grid.EnableEditing( False )
		self.load_grid.EnableGridLines( True )
		self.load_grid.EnableDragGridSize( False )
		self.load_grid.SetMargins( 0, 0 )

		# Columns
		self.load_grid.EnableDragColMove( False )
		self.load_grid.EnableDragColSize( True )
		self.load_grid.SetColLabelSize( 30 )
		self.load_grid.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.load_grid.EnableDragRowSize( True )
		self.load_grid.SetRowLabelSize( 80 )
		self.load_grid.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Label Appearance

		# Cell Defaults
		self.load_grid.SetDefaultCellBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNHIGHLIGHT ) )
		self.load_grid.SetDefaultCellFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		self.load_grid.SetDefaultCellAlignment( wx.ALIGN_CENTER, wx.ALIGN_TOP )
		bSizer1411.Add( self.load_grid, 0, wx.ALL, 5 )

		self.overwatch_button = wx.Button( self.m_panel2, wx.ID_ANY, u"See full statistics in OverWatch", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer1411.Add( self.overwatch_button, 0, wx.ALL, 5 )


		bSizer8.Add( bSizer1411, 1, wx.EXPAND, 5 )

		bSizer141 = wx.BoxSizer( wx.VERTICAL )

		self.qstat_viewlist = wx.dataview.DataViewListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.qstat_viewlist.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.qstat_viewlist.SetMinSize( wx.Size( 800,250 ) )

		bSizer141.Add( self.qstat_viewlist, 0, wx.ALL, 5 )

		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText8 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Scheduler Messages", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText8.Wrap( -1 )

		bSizer16.Add( self.m_staticText8, 0, wx.ALL, 5 )


		bSizer16.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_checkBox_allmsg = wx.CheckBox( self.m_panel2, wx.ID_ANY, u"All Messages", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.m_checkBox_allmsg, 0, wx.ALL, 5 )


		bSizer141.Add( bSizer16, 0, wx.EXPAND, 5 )

		self.scheduler_msg_viewlist = wx.dataview.DataViewListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_HORIZ_RULES|wx.dataview.DV_ROW_LINES|wx.dataview.DV_VARIABLE_LINE_HEIGHT|wx.dataview.DV_VERT_RULES|wx.HSCROLL|wx.VSCROLL )
		self.scheduler_msg_viewlist.SetFont( wx.Font( 9, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial" ) )
		self.scheduler_msg_viewlist.SetMinSize( wx.Size( 800,200 ) )

		bSizer141.Add( self.scheduler_msg_viewlist, 0, wx.ALL, 5 )


		bSizer8.Add( bSizer141, 1, wx.EXPAND, 5 )


		bSizer1.Add( bSizer8, 1, wx.EXPAND, 5 )

		self.m_staticline11 = wx.StaticLine( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )

		ButtonSizer = wx.BoxSizer( wx.HORIZONTAL )

		bSizer28 = wx.BoxSizer( wx.VERTICAL )


		bSizer28.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		ButtonSizer.Add( bSizer28, 1, wx.ALL, 5 )

		bSizer26 = wx.BoxSizer( wx.HORIZONTAL )

		self.save_button = wx.Button( self.m_panel2, wx.ID_ANY, u"Save settings as default", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer26.Add( self.save_button, 0, wx.ALL, 5 )

		self.reset_button = wx.Button( self.m_panel2, wx.ID_ANY, u"Reset factory settings", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer26.Add( self.reset_button, 0, wx.ALL, 5 )

		bSizer29 = wx.BoxSizer( wx.VERTICAL )

		self.close_button = wx.Button( self.m_panel2, wx.ID_ANY, u"Close", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer29.Add( self.close_button, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


		bSizer26.Add( bSizer29, 1, wx.EXPAND, 5 )


		ButtonSizer.Add( bSizer26, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( ButtonSizer, 0, wx.EXPAND, 5 )


		self.m_panel2.SetSizer( bSizer1 )
		self.m_panel2.Layout()
		bSizer1.Fit( self.m_panel2 )
		self.m_notebook2.AddPage( self.m_panel2, u"Launcher", True )
		self.m_panel3 = wx.Panel( self.m_notebook2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer23 = wx.BoxSizer( wx.VERTICAL )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )

		self.user_build_viewlist = wx.dataview.DataViewListCtrl( self.m_panel3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.user_build_viewlist.SetMinSize( wx.Size( 800,450 ) )

		bSizer17.Add( self.user_build_viewlist, 0, wx.ALL, 5 )


		bSizer23.Add( bSizer17, 0, wx.EXPAND, 5 )

		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.delete_build_button = wx.Button( self.m_panel3, wx.ID_ANY, u"Delete Selected Row", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.delete_build_button, 0, wx.ALL, 5 )

		self.add_build_button = wx.Button( self.m_panel3, wx.ID_ANY, u"Add New Build", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer18.Add( self.add_build_button, 0, wx.ALL, 5 )


		bSizer18.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer23.Add( bSizer18, 1, wx.EXPAND, 5 )


		self.m_panel3.SetSizer( bSizer23 )
		self.m_panel3.Layout()
		bSizer23.Fit( self.m_panel3 )
		self.m_notebook2.AddPage( self.m_panel3, u"User-specific builds", False )

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
		self.m_grid1.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

		# Rows
		self.m_grid1.EnableDragRowSize( True )
		self.m_grid1.SetRowLabelSize( 80 )
		self.m_grid1.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

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
		self.submit_mode_radiobox.Bind( wx.EVT_RADIOBOX, self.select_mode )
		self.queue_dropmenu.Bind( wx.EVT_COMBOBOX, self.select_queue )
		self.pe_dropmenu.Bind( wx.EVT_COMBOBOX, self.select_pe )
		self.reserved_checkbox.Bind( wx.EVT_CHECKBOX, self.on_reserve_check )
		self.set_path_button.Bind( wx.EVT_BUTTON, self.set_project_path )
		self.m_button1.Bind( wx.EVT_BUTTON, self.click_launch )
		self.advanced_checkbox.Bind( wx.EVT_CHECKBOX, self.on_advanced_check )
		self.overwatch_button.Bind( wx.EVT_BUTTON, self.submit_overwatch_thread )
		self.qstat_viewlist.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.leftclick_processtable, id = wx.ID_ANY )
		self.m_checkBox_allmsg.Bind( wx.EVT_CHECKBOX, self.m_update_msg_list )
		self.scheduler_msg_viewlist.Bind( wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self.rmb_on_scheduler_msg_list, id = wx.ID_ANY )
		self.save_button.Bind( wx.EVT_BUTTON, self.save_user_settings )
		self.reset_button.Bind( wx.EVT_BUTTON, self.reset_settings )
		self.close_button.Bind( wx.EVT_BUTTON, self.shutdown_app )
		self.delete_build_button.Bind( wx.EVT_BUTTON, self.delete_row )
		self.add_build_button.Bind( wx.EVT_BUTTON, self.add_new_build )

	def __del__( self ):
		self.m_mgr.UnInit()



	# Virtual event handlers, overide them in your derived class
	def shutdown_app( self, event ):
		event.Skip()

	def select_mode( self, event ):
		event.Skip()

	def select_queue( self, event ):
		event.Skip()

	def select_pe( self, event ):
		event.Skip()

	def on_reserve_check( self, event ):
		event.Skip()

	def set_project_path( self, event ):
		event.Skip()

	def click_launch( self, event ):
		event.Skip()

	def on_advanced_check( self, event ):
		event.Skip()

	def submit_overwatch_thread( self, event ):
		event.Skip()

	def leftclick_processtable( self, event ):
		event.Skip()

	def m_update_msg_list( self, event ):
		event.Skip()

	def rmb_on_scheduler_msg_list( self, event ):
		event.Skip()

	def save_user_settings( self, event ):
		event.Skip()

	def reset_settings( self, event ):
		event.Skip()


	def delete_row( self, event ):
		event.Skip()

	def add_new_build( self, event ):
		event.Skip()


