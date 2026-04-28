# Git的使用

## 一. Git几个重要基础概念 
### 工作区、暂存区、本地git仓库 
1. **工作目录** ：就是我创建的那个文件夹，放着我的所有相关文件 
2. **暂存区** ：缓存区，使用`git add`命令，告诉Git哪些是我修改的文件或者说是准备提交的文件 
3. **Git仓库** ： 就是我放着所有提交记录的东西 
   >git仓库是说在`git init`命令之后会产生一个名为`.git`的隐藏文件夹,位于我的根目录下.  
   >这个文件夹包含了项目版本控制所有的数据和配置

### 远程仓库
1. 就是托管在远程服务器\(GitHub\)上面的仓库,用于多人协作 
2. 常用的命令有:  
   ```python
   git clone # 拉取并建立本地仓库 
   git push # 将本地已经提交(commit)的东西提交到远程仓库
   ``` 

### 简要的工作流程
- 工作区 -> git add -> 暂存区  
- 暂存区 -> git commit -> 本地仓库(产生提交,本地仓库记录,存在.git)  
- 本地仓库 -> git push -> 将本地仓库的提交(commit)推送到远端仓库(github)  

## 二、 项目开始初期
### 1.创建本地仓库
1. 使用命令行工具 **(gitbash)** 进入项目文件夹位置   
   `cd /path/to/your/project-floder`   
2. 初始化git仓库,目前已经进入了这个项目文件夹,就在这个位置执行git命令 `git init`  
   成功标志:  `Initialized empty Git repository in /path/to/your/project-folder/.git/`&emsp;从此文件夹就具备了版本控制的能力  

### 2.与远程仓库进行关联绑定
1. 在远程平台创建仓库,得到仓库URL命令提示  
   - 注意:有时候创建的时候不需要让github帮我初始化README文件,.gitignore或者license(因为本地仓库里面可能已经有了这些文件,会造成冲突)  

2. 将本地仓库和远程仓库进行关联  
   - 使用`git remote add`命令,这边假设远程仓库的URL是`https://github.com/yourname/my-project.git`  
   1. 进行关联(在本地仓库执行命令)`git remote add origin https://github.com/yourname/my-project.git`  
   **origin** 是远程仓库的默认别名,远程仓库的别名是方便后续的推送操作。如果没有远程仓库的别名，每次推送代码都要带上远程仓库的URL，有了别名，git就会将别名自动替换成远程仓库的URL,`git push origin main`
   2. 确认关联 `git remote -v` ,看见**origin**和URL就是成功了 
   3. 同一个远程仓库的别名对不同的开发成员来说是相互独立的，但是为了沟通成本，远程仓库的命名通常都是origin  
   4. 远程仓库的别名的重命名  

3. 将本地代码\(就是将提交记录commit\)推送到远程仓库 
   - `git push -u origin main`  
   - **-u**: 告诉git将***本地的main***分支和***远程的origin仓库***联系起来  
   - **origin main**: 
   - 在校园网环境下可能需要关掉VPN  

## 三、 更新文件  
1. **所有更新的文件**都要及时存入*暂存区*，如果一个文件已经存入暂存区了，但是对这个文件又进行了一次修改，再次执行`git add`命令会将新修改的文件覆盖上次的修改版本。 
&emsp;  
2. 如果一次修改了多个文件，想要一次性把所有修改过的文件都加到暂存区，可以直接执行`git add .`\(**粗暴提交所有修改过的文件**\)，或者是`git add 文件名1 文件名2.....`    
&emsp;  
3. 执行命令的时候推荐在项目根目录位置进行执行  
&emsp;  


## 四、下载别人的项目文件
在本地文件夹用git bash 打开，执行`git clone`命令就行，还可以指定在本地的项目文件夹名字，比如`git clone https://github.com/user/repo-name.git MyLocalRepo`


## 五、远程仓库的版本比本地的版本要新，怎么在不改动自己的修改的情况下跟新自己本地的版本  
现在的场景是这样的，在**我开发一半的时候**（我还没开发完成，也就是还没有把我的更新push到远端），但是**我的同伴更新了仓库**。  
我现在希望我接下来的开发是基于最新的仓库状态，那我应该怎么在vscode中执行git命令，**保证我之前的开发没有丢失同时又更新了本地仓库的版本**。  
**简化场景描述：** 先把手上的活藏起来，把地基更换，再把手头的活搬回来。  
-  方法一、在vscode的终端使用git命令（使用ctrl + ~快捷键调用终端）
  1. 把当前的修改隐藏 git stash
    - 执行完后，刚才写一半的代码不见了，回到了上次提交的状态
  2.  拉取远程最新代码
    - git pull origin <你的分支名>，如果目前我就在当前分支的话也可以直接git pull
    - 执行完后本地代码就会更新了
  3. 把之前隐藏的修改取出来
    - git stash pop
    - 之前写一半的代码就会回来覆盖在最新的代码之上

- 方法二、使用vscode内置的git图形操作界面
  1. 

- **如果出现冲突：**（在最后一步git stash pop的时候）可能会出现冲突，就是你之前的修改的某些地方，同伴也修改了。这是vscode会弹出冲突提示，根据显示来选择你是要保留谁的修改。



## 六、vscode设置代理
有时候在vscode里面进行git操作的时候可能提示失败，是因为代理的问题，需要设置代理。  
1. 准备工作：  
    - 查找vpn的端口
2. 区分全局设置和单一项目设置：  
    * 全局设置的命令里面有一个`--global`参数;  
    * 全局设置就是只要设置成功以后每个项目都会走这个代理（开着VPN的时候），当你关掉VPN的时候就需要手动取消代理
    * 单一项目设置就是没有`--global`参数，只会影响到当前项目，不会让别的项目也走代理  
3. 需要的命令
    - 全局设置
     ```
      # 设置 HTTP 和 HTTPS 代理 (注意把 7890 换成你实际的代理端口)
      git config --global http.proxy http://127.0.0.1:7890
      git config --global https.proxy http://127.0.0.1:7890
     ```
    - 取消代理（单一项目取消代理去掉--global）  
     ```
      git config --global --unset http.proxy
      git config --global --unset https.proxy
     ```
    - 检查当前代理状态
     ```
      git config --global -l
      看列表里面有没有http.proxy
     ```
    - Schannel和OpenSSL
     ```
      git config --global http.sslBackend openssl（更改成OpenSSL）
      git config --global --unset http.sslBackend（恢复Schannel）
     ```