# Three.js + VRM 基礎学習メモ

## Three.jsとは

ブラウザで3Dグラフィックスを描画するJavaScriptライブラリ（WebGLのラッパー）。3D表示に最低限必要な3要素は共通して以下：

- **Scene**：3Dオブジェクトを配置する空間
- **Camera**：どこから見るか（`PerspectiveCamera`は遠近感のある一般的なカメラ）
- **Renderer**：Sceneをレンダリングして`<canvas>`に描画する

```js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(30, width / height, 0.1, 20);
const renderer = new THREE.WebGLRenderer({ antialias: true });
```

`requestAnimationFrame`でループを回し、毎フレーム`renderer.render(scene, camera)`を呼ぶことで動くアニメーションになる。

## VRMとは

VRoid Studioなどで作られる、アニメ調3Dアバターの標準フォーマット。実体はglTF（3D業界標準フォーマット）にVRM独自の拡張情報（人型の骨格構造、表情、マテリアル等）を追加したもの。

```js
const loader = new GLTFLoader();
loader.register((parser) => new VRMLoaderPlugin(parser));
loader.load(modelUrl, (gltf) => {
  const vrm = gltf.userData.vrm; // VRM独自の情報はここに入っている
  scene.add(vrm.scene);
});
```

- `vrm.humanoid`：人型の骨格（頭・腕・脚など）を統一された名前で扱える仕組み
- `vrm.update(delta)`：表情・視線・物理演算などVRM独自の要素を毎フレーム更新する（`renderer.render`とは別に呼ぶ必要がある）

## MToonマテリアル

VRMモデルは標準でMToon（トゥーン/セルシェーディング用マテリアル）を使っているため、特別な設定なしで「アニメ的な平面的な陰影」の見た目になる。

## React 18 StrictModeとの注意点

開発モードではStrictModeが`useEffect`を意図的に2回実行する（副作用のバグ検出のため）。非同期処理（`loader.load`など）の中で`useEffect`のクリーンアップ後に状態更新を呼ぶと、破棄されたはずの古いシーンの結果が紛れ込むことがある。`cancelled`フラグを立てて、クリーンアップ後のコールバックを無視するガードが必要。
