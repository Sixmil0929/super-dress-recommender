# Git Branch

## 一、使用分支
使用原则，一个任务就应该对应一个分支（无论这个任务有多么小）  
分支的作用：  
1. 开发新功能  
2. 修复bug  
3. 在尝试别的实现方法时（比如我想要从fastapi转换成flask）  


## 二、常见流程  
- a接到了开发任务，他就要去创建一个新的分支来管理他的开发代码    
1. `git checkout main`    
   让本地的git指向本地的main

2. `git pull origin main`
   origin是远程仓库的别名，这一步的作用是确保本地的main分支跟远程仓库的main分支同步，使我们的新开发是基于最新状态的开发

3. `git checkout -b feature/new-task`
   创建新分支，命名成feature/new-task，同时git不再指向main而是这个新分支  
   分支的命名有一套标准，可以在使用的时候再看   
---
- 接下来a就开始进行他的开发任务，在他的开发过程中他应该时不时地把自己的进度推送到远端，这样既达到了备份自己代码的目的，同时又可以伙伴之间的沟通    

4. 
    ``` python
    git add . # 将所有修改过的代码提交到暂存区
    git commit -m "message" # 将暂存区的代码提交，git就会产生一个新的节点  
    git push -u origin feature/new-task 
    # 如果远端没有这个feature/new-task分支就会创建新分支，而且新分支命名成feature/new-task
    # git 会将本地当前指向的这个分支(feature/new-task)推送到远端仓库的feature/new-task分支
    # -u 参数的作用是将本地和远端的这两个分支绑定，以后本地git再指向这个分支的时候git就自动明白要把新推送push到远端的这个分支
    ```
5. 每天的习惯或者说是在得知仓库更新的时候   
    ``` python
        # 更新自己的main分支
        git checkout main
        git pull origin main

        # 返回自己的开发分支，并更新地基
        git checkout feature/my-task  
        git rebase main # 这边最好不要用merge，虽然也可以  

        M1 --- M2 (main)
            \
            F1 --- F2 (feature)
        
    ```
    * rebase的使用：只有你一个人在开发的分支，而且是在自己电脑上的  
    * 对于主分支main和**多人共同开发的分支**应该使用 git merge  
    * 自己在玩用rebase，多人合作使用merge  
    * rebase之后，远端的相对应的分支还是在旧版本的地基之上，本地的提交是在新地基上的，所以这时候想要把本地的分支push到远端的相对应的分支上是会失败的  
    * rebase之后想要成功push就需要`git push origin branchName --force`,这样远端的相对应分支也会跟换地基，并且跟你的分支保持同步
    * ***千万千万不能对main分支（本地和远端都是）使用git rebase，只要是多人开发的分支都不能使用git rebase。
***
---

- 现在a开发完成了，接下来要做的事情是
6. 首先确保自己的所有更改已经commit，形成这个分支的最后一个节点  
7. 再次更新main分支，重复一下上面的 **“每天习惯”** （单人分支使用rebase，多人分支使用merge）
8. 确认无误之后push到远端的相对应的分支上  
9. **重点**：创建PR/MR。别人检查无误之后就可以merge


- 现在开发了，想要合并了，就需要在仓库发起pull request或者是merge request，不要尝试在本地合并自己的分支到main

---

- 合并完了之后应该删除分支  
10. 网页端会提示**Delete Branch**,点击它就可以删除远端分支  
11. 回到本地清理这个分支  
    ```python
    git checkout main
    git pull origin main # 会把刚才合并进去的代码拉回来
    git branch -d branchName
    ```
----

