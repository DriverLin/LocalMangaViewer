介绍：
==
	简单的漫画浏览器
	展示漫画画廊
	根据TAG和关键词检索画廊
	使用浏览器浏览画廊并下载

使用说明
==
	服务端只需要实现get请求即可，直接用IIS就挺好的
	也可以使用pythonServer.py来启动 添加了简单验证功能 key在脚本里面
	pythonServer.py依赖bottle
	修改具体内容可以查看pythonServer.py文件
如何添加画廊
==
	理想情况是，移动端开，PC端开，使用DownloadFromRemote.py来同步
	手动添加画廊需要添加封面到cover，修改data.js ，画廊目录下创建profile.js ，画廊文件放入Gallarys
	封面格式为jpg
	android端通过'update.py'和'cj创建画廊配置文件'可以在Ehviewer目录下直接更新
	'update.py'用于通过目录下的.ehviewer文件爬取相关信息并保存到./json目录下
	'update.py'使用的的cookie自行填写
	'update.py'依赖vthread
	'cj创建画廊配置文件' 读取./json目录下配置文件 创建profile.js 直接修改data.js 添加封面 
	获取tag功能需要去获取cookie并手动修改update.py里cookie信息
相关文件
==
	data.js //画廊数据
	{
		gid_token:{
			文件路径:'path'
			画廊名称:'path'
			tags:{
				{类:[值，]},
			}
		},
	}

	cover文件夹 存放封面
	Gallarys文件夹 存放画廊
	profile.js //画廊配置信息
	{
	pics:[图片文件数组]，
	info:{
		文件名:[]
		画廊名:[]
		gid:[]
		toekn:[]
		作者:[]
		角色:[]
		女性:[]
		团体:[]
		语言:[]
		男性:[]
		杂项:[]
		原作:[]
		重分类:[]
		}
	}
