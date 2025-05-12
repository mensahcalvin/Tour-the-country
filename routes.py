from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from models import db, User, Post, Comment, Category, Tag
from slugify import slugify

blog = Blueprint('blog', __name__)

@blog.route('/')
def home():
    # Get featured posts
    featured_posts = Post.query.filter_by(is_published=True).order_by(Post.views.desc()).limit(3).all()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(is_published=True).order_by(Post.date_posted.desc()).limit(6).all()
    
    # Get categories with post counts
    categories = Category.query.join(Post).group_by(Category.id).all()
    
    return render_template('home.html',
                         featured_posts=featured_posts,
                         recent_posts=recent_posts,
                         categories=categories)

# Blog listing page
@blog.route('/blog')
def blog_list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    tag = request.args.get('tag')
    search_query = request.args.get('q')
    
    # Base query
    query = Post.query.filter_by(is_published=True)
    
    # Apply filters
    if category:
        query = query.filter(Post.category.has(slug=category))
    if tag:
        query = query.filter(Post.tags.any(slug=tag))
    if search_query:
        query = query.filter(
            (Post.title.ilike(f'%{search_query}%')) |
            (Post.content.ilike(f'%{search_query}%'))
        )
    
    # Get paginated posts
    posts = query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    
    # Get categories with post counts
    categories = Category.query.join(Post).group_by(Category.id).all()
    
    # Get recent posts
    recent_posts = Post.query.filter_by(is_published=True).order_by(Post.date_posted.desc()).limit(3).all()
    
    # Get popular tags
    tags = Tag.query.join(Post.tags).group_by(Tag.id).all()
    
    return render_template('blog.html',
                         posts=posts,
                         categories=categories,
                         recent_posts=recent_posts,
                         tags=tags)

# Individual post page
@blog.route('/post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Increment view count
    post.views += 1
    db.session.commit()
    
    # Get related posts
    related_posts = Post.query.filter(
        Post.category_id == post.category_id,
        Post.id != post.id,
        Post.is_published == True
    ).order_by(Post.date_posted.desc()).limit(2).all()
    
    return render_template('post.html',
                         post=post,
                         related_posts=related_posts)

# Add comment
@blog.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    parent_id = request.form.get('parent_id', type=int)
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('blog.post', post_id=post_id))
    
    comment = Comment(
        content=content,
        author_id=current_user.id,
        post_id=post_id,
        parent_id=parent_id if parent_id else None
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('blog.post', post_id=post_id))

# Delete comment
@blog.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if current_user.id != comment.author_id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'success': True})

# Create new post (admin/author only)
@blog.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    if not current_user.is_admin and current_user.role != 'author':
        flash('You do not have permission to create posts', 'error')
        return redirect(url_for('blog.blog_list'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        tags = request.form.getlist('tags')
        
        if not all([title, content, category_id]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('blog.new_post'))
        
        # Handle image upload
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/uploads', filename))
                image_url = f'/static/uploads/{filename}'
        
        # Create post
        post = Post(
            title=title,
            slug=slugify(title),
            content=content,
            excerpt=content[:200] + '...' if len(content) > 200 else content,
            image_url=image_url,
            author_id=current_user.id,
            category_id=category_id
        )
        
        # Add tags
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, slug=slugify(tag_name))
                db.session.add(tag)
            post.tags.append(tag)
        
        db.session.add(post)
        db.session.commit()
        
        flash('Post created successfully', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('new_post.html', categories=categories, tags=tags)

# Edit post
@blog.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.id != post.author_id and not current_user.is_admin:
        flash('You do not have permission to edit this post', 'error')
        return redirect(url_for('blog.post', post_id=post_id))
    
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.category_id = request.form.get('category_id')
        post.slug = slugify(post.title)
        post.excerpt = post.content[:200] + '...' if len(post.content) > 200 else post.content
        
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/uploads', filename))
                post.image_url = f'/static/uploads/{filename}'
        
        # Update tags
        post.tags = []
        for tag_name in request.form.getlist('tags'):
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name, slug=slugify(tag_name))
                db.session.add(tag)
            post.tags.append(tag)
        
        db.session.commit()
        
        flash('Post updated successfully', 'success')
        return redirect(url_for('blog.post', post_id=post.id))
    
    categories = Category.query.all()
    tags = Tag.query.all()
    return render_template('edit_post.html', post=post, categories=categories, tags=tags)

# Delete post
@blog.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.id != post.author_id and not current_user.is_admin:
        flash('You do not have permission to delete this post', 'error')
        return redirect(url_for('blog.post', post_id=post_id))
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Post deleted successfully', 'success')
    return redirect(url_for('blog.blog_list')) 