import { Navigate, createBrowserRouter } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import FileLibPage from "./pages/FileLibPage";
import FilesPage from "./pages/FileLibPage/files";
import FlowPage from "./pages/FlowPage";
import ModelPage from "./pages/ModelPage";
import Doc from "./pages/ModelPage/doc";
import Report from "./pages/Report";
import SkillChatPage from "./pages/ChatAppPage";
import ChatShare from "./pages/ChatAppPage/chatShare";
import ChatPro from "./pages/ChatAppPage/chatWebview";
import SkillAssisPage from "./pages/SkillPage/tabAssistant";
import EditAssistantPage from "./pages/SkillPage/editAssistant";
import SkillsPage from "./pages/SkillPage/tabSkills";
import SkillToolsPage from "./pages/SkillPage/tabTools";
import L2Edit from "./pages/SkillPage/l2Edit";
import SystemPage from "./pages/SystemPage";
import BuildLayout from "./layout/BuildLayout";
import Templates from "./pages/SkillPage/temps";
import DiffFlowPage from "./pages/DiffFlowPage";
import LogPage from "./pages/LogPage";
import { ErrorBoundary } from "react-error-boundary";
import CrashErrorComponent from "./components/CrashErrorComponent";
import { LoginPage } from "./pages/LoginPage/login";
import { ResetPwdPage } from "./pages/LoginPage/resetPwd";

// react 与 react router dom版本不匹配
// const FileLibPage = lazy(() => import(/* webpackChunkName: "FileLibPage" */ "./pages/FileLibPage"));
// const FilesPage = lazy(() => import(/* webpackChunkName: "FilesPage" */ "./pages/FileLibPage/files"));
// const SkillPage = lazy(() => import(/* webpackChunkName: "SkillPage" */ "./pages/SkillPage"));
// const SkillChatPage = lazy(() => import(/* webpackChunkName: "SkillChatPage" */ "./pages/SkillChatPage"));
// const FileViewPage = lazy(() => import(/* webpackChunkName: "FileViewPage" */ "./pages/FileViewPage"));

const ErrorHoc = ({ Comp }) => {
  return (
    <ErrorBoundary
      onReset={() => window.location.href = window.location.href}
      FallbackComponent={CrashErrorComponent}
    >
      <Comp />
    </ErrorBoundary>
  );
}


const privateRouter = [
  {
    path: "/",
    element: <MainLayout />,
    children: [
      { path: "", element: <SkillChatPage />, },
      { path: "filelib", element: <FileLibPage />, permission: 'knowledge', },
      { path: "filelib/:id", element: <FilesPage />, permission: 'knowledge', },
      {
        path: "build",
        element: <BuildLayout />,
        permission: 'build',
        children: [
          { path: "assist", element: <SkillAssisPage /> },
          { path: "skills", element: <SkillsPage /> },
          { path: "tools", element: <SkillToolsPage /> },
          { path: "", element: <Navigate to="assist" replace /> },
        ]
      },
      { path: "build/skill", element: <L2Edit />, permission: 'build', },
      { path: "build/skill/:id/:vid", element: <L2Edit />, permission: 'build', },
      { path: "build/temps", element: <Templates />, permission: 'build', },
      { path: "model", element: <ModelPage />, permission: 'model', },
      { path: "sys", element: <SystemPage /> },
      { path: "log", element: <LogPage /> },
    ],
  },
  { path: "model/doc", element: <Doc /> },
  {
    path: "/flow/:id/",
    children: [
      { path: "", element: <ErrorHoc Comp={FlowPage} /> }
    ]
  },
  {
    path: "/assistant/:id/",
    children: [
      { path: "", element: <EditAssistantPage /> }
    ]
  },
  // 独立会话页
  { path: "/chat", element: <SkillChatPage /> },
  { path: "/chat/:id/", element: <ChatShare /> },
  { path: "/chatpro/:id", element: <ChatPro /> },
  { path: "/report/:id/", element: <Report /> },
  { path: "/diff/:id/:vid/:cid", element: <ErrorHoc Comp={DiffFlowPage} /> },
  { path: "/reset", element: <ResetPwdPage /> },
  // { path: "/test", element: <Test /> },
  { path: "*", element: <Navigate to="/" replace /> }
]

export const getPrivateRouter = (permissions) => {
  const filterMenuItem = (_privateRouter) => {
    const result = _privateRouter.reduce((res, cur) => {
      // 递归
      if (cur.children?.length) {
        cur.children = filterMenuItem(cur.children)
      }

      const { permission, ...other } = cur
      if (permission && !permissions.includes(permission)) {
        return res
      }

      res.push(other)
      return res
    }, [])

    return result
  }

  return createBrowserRouter(permissions ? filterMenuItem(privateRouter) : [],
    {
      // basename: "/pro"
    })
}

export const publicRouter = createBrowserRouter([
  { path: "/", element: <LoginPage /> },
  { path: "/reset", element: <ResetPwdPage /> },
  { path: "*", element: <LoginPage /> }
],
  {
    // basename: "/pro"
  })
